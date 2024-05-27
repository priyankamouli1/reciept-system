const loginBtn = document.querySelector("#login");
const registerBtn = document.querySelector("#register");
const loginForm = document.querySelector(".login-form");
const registerForm = document.querySelector(".register-form");
console.log("script.js loaded successfully");

loginBtn.addEventListener("click", () => {
  loginBtn.style.backgroundColor = "#d5cb3d";
  registerBtn.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
  loginForm.style.left = "50%";
  registerForm.style.left = "-50%";
  loginForm.style.opacity = 1;
  registerForm.style.opacity = 0;
  document.querySelector(".col-1").style.borderRadius = "0 30% 20% 0";
});

registerBtn.addEventListener("click", () => {
  loginBtn.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
  registerBtn.style.backgroundColor = "#d5cb3d";
  loginForm.style.left = "150%";
  registerForm.style.left = "50%";
  loginForm.style.opacity = 0;
  registerForm.style.opacity = 1;
  document.querySelector(".col-1").style.borderRadius = "0 20% 30% 0";
});