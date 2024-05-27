// Get form elements
const signInForm = document.getElementById('signInForm');
const signUpForm = document.getElementById('signUpForm');

// Add event listener for sign in form
signInForm.addEventListener('submit', function(event) {
  event.preventDefault();
  const login = document.getElementById('login').value;
  const password = document.getElementById('password').value;
  
  // Here you can add the code to send the login and password to your server
  console.log(`Login: ${login}, Password: ${password}`);
});

// Add event listener for sign up form
signUpForm.addEventListener('submit', function(event) {
  event.preventDefault();
  const login = document.getElementById('signUpLogin').value;
  const password = document.getElementById('signUpPassword').value;
  
  // Here you can add the code to send the login and password to your server
  console.log(`Login: ${login}, Password: ${password}`);
});