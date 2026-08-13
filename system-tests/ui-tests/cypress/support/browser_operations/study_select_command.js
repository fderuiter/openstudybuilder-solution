Cypress.Commands.add("selectTestStudy", (study) => {
  cy.request(Cypress.env("API") + "/studies/" + study).then((response) => {
    window.sessionStorage.setItem("selectedStudy", JSON.stringify(response.body));
  });
});
