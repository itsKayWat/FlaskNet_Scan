export class AppError extends Error {
  constructor(message, code, details = null) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.details = details
  }
}

export const errorCodes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  RATE_LIMIT: 'RATE_LIMIT'
}

export const handleError = (error) => {
  if (error instanceof AppError) {
    return {
      message: error.message,
      code: error.code,
      details: error.details
    }
  }

  // Axios error
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case 401:
        return new AppError(
          'Authentication required',
          errorCodes.AUTH_ERROR
        )
        
      case 403:
        return new AppError(
          'Permission denied',
          errorCodes.PERMISSION_DENIED
        )
        
      case 404:
        return new AppError(
          'Resource not found',
          errorCodes.NOT_FOUND
        )
        
      case 422:
        return new AppError(
          'Validation error',
          errorCodes.VALIDATION_ERROR,
          data.errors
        )
        
      case 429:
        return new AppError(
          'Rate limit exceeded',
          errorCodes.RATE_LIMIT
        )
        
      default:
        return new AppError(
          'Server error',
          errorCodes.SERVER_ERROR,
          data
        )
    }
  }

  // Network error
  if (error.request) {
    return new AppError(
      'Network error',
      errorCodes.NETWORK_ERROR
    )
  }

  // Unknown error
  return new AppError(
    'An unexpected error occurred',
    errorCodes.SERVER_ERROR
  )
}

export const formatValidationErrors = (errors) => {
  if (!errors) return {}
  
  return Object.entries(errors).reduce((acc, [field, messages]) => {
    acc[field] = Array.isArray(messages) ? messages[0] : messages
    return acc
  }, {})
} 