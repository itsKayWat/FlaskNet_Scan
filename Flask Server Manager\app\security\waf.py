from flask import request, abort
import re
from typing import List, Dict, Optional
import ipaddress
from dataclasses import dataclass
import redis
from datetime import datetime, timedelta

@dataclass
class WAFRule:
    id: str
    pattern: str
    description: str
    severity: str
    enabled: bool = True

class WAF:
    def __init__(self, app=None):
        self.app = app
        self.rules: List[WAFRule] = []
        self.blacklist: List[ipaddress.IPv4Network] = []
        self.whitelist: List[ipaddress.IPv4Network] = []
        self.redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_WAF_DB']
        )
        self.load_rules()

    def load_rules(self):
        # SQL Injection rules
        self.rules.append(WAFRule(
            id='SQL001',
            pattern=r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION).*FROM',
            description='SQL Injection attempt',
            severity='HIGH'
        ))

        # XSS rules
        self.rules.append(WAFRule(
            id='XSS001',
            pattern=r'(?i)<script.*?>.*?</script.*?>',
            description='Cross-site scripting attempt',
            severity='HIGH'
        ))

        # Path traversal rules
        self.rules.append(WAFRule(
            id='PTR001',
            pattern=r'\.\./',
            description='Path traversal attempt',
            severity='HIGH'
        ))

    def check_request(self, request) -> Optional[Dict]:
        # Check IP restrictions
        if not self._check_ip(request.remote_addr):
            return {
                'blocked': True,
                'reason': 'IP address blocked',
                'rule_id': 'IP001'
            }

        # Check rate limits
        if not self._check_rate_limit(request):
            return {
                'blocked': True,
                'reason': 'Rate limit exceeded',
                'rule_id': 'RATE001'
            }

        # Check request parameters
        params = self._get_request_params(request)
        for param in params:
            for rule in self.rules:
                if rule.enabled and re.search(rule.pattern, param):
                    self._log_violation(rule, request, param)
                    return {
                        'blocked': True,
                        'reason': rule.description,
                        'rule_id': rule.id
                    }

        return None

    def _check_ip(self, ip: str) -> bool:
        try:
            ip_addr = ipaddress.ip_address(ip)
            
            # Check blacklist
            if any(ip_addr in network for network in self.blacklist):
                return False
                
            # If whitelist is empty, allow all non-blacklisted IPs
            if not self.whitelist:
                return True
                
            # Check whitelist
            return any(ip_addr in network for network in self.whitelist)
            
        except ValueError:
            return False

    def _check_rate_limit(self, request) -> bool:
        key = f"ratelimit:{request.remote_addr}"
        pipe = self.redis_client.pipeline()
        
        now = datetime.utcnow()
        window_size = 60  # 1 minute window
        max_requests = 100  # Maximum requests per window
        
        # Clean up old entries and add new request
        pipe.zremrangebyscore(key, 0, now.timestamp() - window_size)
        pipe.zadd(key, {str(now.timestamp()): now.timestamp()})
        pipe.zcard(key)
        pipe.expire(key, window_size)
        
        results = pipe.execute()
        request_count = results[2]
        
        return request_count <= max_requests

    def _get_request_params(self, request) -> List[str]:
        params = []
        
        # Check URL parameters
        if request.args:
            params.extend(request.args.values())
            
        # Check form data
        if request.form:
            params.extend(request.form.values())
            
        # Check JSON data
        if request.is_json:
            try:
                json_data = request.get_json()
                if isinstance(json_data, dict):
                    params.extend(str(v) for v in json_data.values())
            except Exception:
                pass
                
        return params

    def _log_violation(self, rule: WAFRule, request, param: str):
        violation = {
            'timestamp': datetime.utcnow().isoformat(),
            'rule_id': rule.id,
            'severity': rule.severity,
            'ip_address': request.remote_addr,
            'url': request.url,
            'method': request.method,
            'matched_param': param,
            'headers': dict(request.headers)
        }
        
        self.redis_client.lpush(
            'waf:violations',
            str(violation)
        )
        self.redis_client.ltrim('waf:violations', 0, 999)  # Keep last 1000 violations 