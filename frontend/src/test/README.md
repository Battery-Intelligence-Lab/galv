# Galv Testing Strategy

## Unit Testing

Unit testing is done using the [Jest](https://jestjs.io/) framework. 
The tests are located in the `frontend/src/test` directory. 
The tests are run using the command `npm test` in the `frontend` directory.

### Mocking and Scoping

Components are tested as a complete, isolated component. 
There are, however, a few shared custom components that other components use.
These components are included in their actual form, and not mocked, 
while the rest of the components are mocked in `frontend/src/test/__mocks__`.

The components that are not mocked are:
- `ActionButtons`
  - used by many components to trigger CRUD actions
- `AsyncTable`
  - used by many components to display data in a table
Note that any errors introduced in these components will affect several tests.

Additionally, the `APIConnection` module's default export, 
an instance of the `APIConnection` class, is mocked on a case-by-case basis in order to return appropriate data. 
Some tests require mocking the `APIConnection` login method to return a successful login.

### Fixtures

API response fixtures are located in `frontend/src/test/__fixtures__`.
Where a fixture's content would appear in another fixture, only the wrapping fixture is used.
For example, the details of a fake administrator are included in the `user-sets` of the `harvesters.json` fixture,
so no `user.json` fixture is needed.

### What to Test

Roughly following [this guide](https://daveceddia.com/what-to-test-in-react-app/),
tests are expected to cover the following:
- Rendering
- Calling the API to Create/Update/Delete data
- Spawning child components (though those components themselves are mocked)
- Any specific issues that a patch is submitted to address

## End-to-End Testing

End-to-end testing is done using the [Cypress](https://www.cypress.io/) framework.