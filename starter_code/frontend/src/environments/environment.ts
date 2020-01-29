/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000/', // the running FLASK api server url
  auth0: {
    url: 'coffeeshop01', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: 'jIGYbbBf8YsDHY0UvAyP4sZ2F7E9A6DT', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:5000', // the base url of the running ionic application. 
  }
};
