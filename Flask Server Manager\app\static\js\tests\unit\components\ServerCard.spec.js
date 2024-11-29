import { mount } from '@vue/test-utils'
import ServerCard from '@/components/ServerCard.vue'
import { createStore } from 'vuex'

describe('ServerCard.vue', () => {
  const createWrapper = (props = {}, store = null) => {
    const defaultProps = {
      server: {
        id: 1,
        name: 'Test Server',
        status: 'running',
        host: 'localhost',
        port: 8080,
        metrics: {
          cpu: 50,
          memory: 60,
          disk: 70
        }
      }
    }

    return mount(ServerCard, {
      props: { ...defaultProps, ...props },
      global: {
        plugins: store ? [store] : [],
        stubs: {
          'line-chart': true
        }
      }
    })
  }

  test('renders server information correctly', () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('.server-title h3').text()).toBe('Test Server')
    expect(wrapper.find('.status-badge').exists()).toBe(true)
  })

  test('toggles details section', async () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('.server-details').exists()).toBe(false)
    
    await wrapper.find('.icon-button').trigger('click')
    expect(wrapper.find('.server-details').exists()).toBe(true)
  })

  test('emits correct events for server actions', async () => {
    const wrapper = createWrapper()
    
    await wrapper.find('[data-test="start-server"]').trigger('click')
    expect(wrapper.emitted('action')).toBeTruthy()
    expect(wrapper.emitted('action')[0]).toEqual(['start'])
  })

  test('displays correct resource usage colors', () => {
    const wrapper = createWrapper({
      server: {
        id: 1,
        name: 'Test Server',
        metrics: {
          cpu: 95, // Critical
          memory: 75, // Warning
          disk: 50 // Normal
        }
      }
    })
    
    const progressBars = wrapper.findAll('.progress')
    expect(progressBars[0].classes()).toContain('critical')
    expect(progressBars[1].classes()).toContain('warning')
    expect(progressBars[2].classes()).toContain('normal')
  })
}) 