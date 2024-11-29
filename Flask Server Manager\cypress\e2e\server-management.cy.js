describe('Server Management', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'password123')
    cy.visit('/servers')
  })

  it('displays server list and performs CRUD operations', () => {
    // Create new server
    cy.get('[data-test="add-server-btn"]').click()
    cy.get('[data-test="server-name"]').type('Test Server')
    cy.get('[data-test="server-host"]').type('localhost')
    cy.get('[data-test="server-port"]').type('8080')
    cy.get('[data-test="submit-server"]').click()

    // Verify server was created
    cy.get('.server-card').should('have.length.at.least', 1)
    cy.contains('Test Server').should('be.visible')

    // Edit server
    cy.get('[data-test="server-menu"]').first().click()
    cy.get('[data-test="edit-server"]').click()
    cy.get('[data-test="server-name"]').clear().type('Updated Server')
    cy.get('[data-test="submit-server"]').click()
    cy.contains('Updated Server').should('be.visible')

    // Delete server
    cy.get('[data-test="server-menu"]').first().click()
    cy.get('[data-test="delete-server"]').click()
    cy.get('[data-test="confirm-delete"]').click()
    cy.contains('Updated Server').should('not.exist')
  })

  it('handles server actions and monitors status', () => {
    // Start server
    cy.get('[data-test="start-server"]').first().click()
    cy.get('.status-badge').should('contain', 'running')
    
    // Monitor metrics
    cy.get('.server-metrics').should('be.visible')
    cy.get('.cpu-usage').should('exist')
    cy.get('.memory-usage').should('exist')
    
    // Stop server
    cy.get('[data-test="stop-server"]').first().click()
    cy.get('.status-badge').should('contain', 'stopped')
  })

  it('filters and sorts servers', () => {
    // Search functionality
    cy.get('[data-test="search-input"]').type('prod')
    cy.get('.server-card').should('have.length.at.least', 1)
    
    // Status filter
    cy.get('[data-test="status-filter"]').select('running')
    cy.get('.server-card').each($card => {
      cy.wrap($card).find('.status-badge').should('contain', 'running')
    })
    
    // Sort by name
    cy.get('[data-test="sort-select"]').select('name')
    cy.get('.server-card').should('be.sorted')
  })

  it('handles errors gracefully', () => {
    // Network error
    cy.intercept('GET', '/api/servers', {
      forceNetworkError: true
    })
    cy.reload()
    cy.get('[data-test="error-message"]')
      .should('contain', 'Network error')
    
    // Invalid input
    cy.get('[data-test="add-server-btn"]').click()
    cy.get('[data-test="submit-server"]').click()
    cy.get('[data-test="validation-error"]').should('be.visible')
  })
}) 