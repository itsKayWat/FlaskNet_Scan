Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: {
      email,
      password
    }
  }).then((response) => {
    window.localStorage.setItem('token', response.body.token)
  })
})

Cypress.Commands.add('createServer', (serverData) => {
  cy.request({
    method: 'POST',
    url: '/api/servers',
    headers: {
      Authorization: `Bearer ${window.localStorage.getItem('token')}`
    },
    body: serverData
  })
})

// Custom assertion for sorted elements
chai.use((_chai, utils) => {
  function assertSorted(elements) {
    const texts = elements.map((i, el) => Cypress.$(el).text().trim())
    const sorted = [...texts].sort()
    expect(texts.toArray()).to.deep.equal(sorted)
  }

  _chai.Assertion.addMethod('sorted', function () {
    assertSorted(this._obj)
  })
}) 