import { createStore } from 'vuex'
import serversModule from '@/store/modules/servers'
import { fetchServers, createServer, updateServer } from '@/api/servers'

// Mock API calls
jest.mock('@/api/servers')

describe('servers store module', () => {
  let store

  beforeEach(() => {
    store = createStore({
      modules: {
        servers: {
          ...serversModule,
          namespaced: true
        }
      }
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('mutations', () => {
    test('SET_SERVERS updates the servers array', () => {
      const servers = [
        { id: 1, name: 'Server 1' },
        { id: 2, name: 'Server 2' }
      ]
      
      store.commit('servers/SET_SERVERS', servers)
      expect(store.state.servers.servers).toEqual(servers)
    })

    test('ADD_SERVER adds a server to the array', () => {
      const newServer = { id: 1, name: 'New Server' }
      
      store.commit('servers/ADD_SERVER', newServer)
      expect(store.state.servers.servers).toContainEqual(newServer)
    })

    test('UPDATE_SERVER updates an existing server', () => {
      const server = { id: 1, name: 'Server 1', status: 'stopped' }
      store.commit('servers/SET_SERVERS', [server])
      
      const update = { id: 1, status: 'running' }
      store.commit('servers/UPDATE_SERVER', update)
      
      expect(store.state.servers.servers[0].status).toBe('running')
    })
  })

  describe('actions', () => {
    test('fetchAllServers calls API and updates state', async () => {
      const servers = [
        { id: 1, name: 'Server 1' },
        { id: 2, name: 'Server 2' }
      ]
      
      fetchServers.mockResolvedValue({ data: servers })
      
      await store.dispatch('servers/fetchAllServers')
      
      expect(fetchServers).toHaveBeenCalled()
      expect(store.state.servers.servers).toEqual(servers)
    })

    test('createNewServer calls API and adds server', async () => {
      const newServer = { name: 'New Server', host: 'localhost' }
      const createdServer = { id: 1, ...newServer }
      
      createServer.mockResolvedValue({ data: createdServer })
      
      await store.dispatch('servers/createNewServer', newServer)
      
      expect(createServer).toHaveBeenCalledWith(newServer)
      expect(store.state.servers.servers).toContainEqual(createdServer)
    })

    test('handles API errors correctly', async () => {
      const error = new Error('API Error')
      fetchServers.mockRejectedValue(error)
      
      await expect(store.dispatch('servers/fetchAllServers'))
        .rejects.toThrow('API Error')
        
      expect(store.state.servers.error).toBe(error.message)
    })
  })

  describe('getters', () => {
    test('filteredServers applies search filter', () => {
      const servers = [
        { id: 1, name: 'Production Server' },
        { id: 2, name: 'Development Server' },
        { id: 3, name: 'Test Server' }
      ]
      
      store.commit('servers/SET_SERVERS', servers)
      store.commit('servers/SET_FILTERS', { search: 'prod' })
      
      const filtered = store.getters['servers/filteredServers']
      expect(filtered).toHaveLength(1)
      expect(filtered[0].name).toBe('Production Server')
    })

    test('serversByStatus returns correct servers', () => {
      const servers = [
        { id: 1, status: 'running' },
        { id: 2, status: 'stopped' },
        { id: 3, status: 'running' }
      ]
      
      store.commit('servers/SET_SERVERS', servers)
      
      const runningServers = store.getters['servers/serversByStatus']('running')
      expect(runningServers).toHaveLength(2)
    })
  })
}) 