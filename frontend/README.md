# spec2spec demo Frontend

This is the folder containing the frontend code for spec2spec demo. It is built using pure JavaScript without using any popular JS frameworks.

This is a simple web interface. As long as you have a modern web browser, you should be able to load this page.

Again, because of its simplicity, there is no special steps to set this up.

## Notes on local deployment

This is by default configured to connect to the backend at `127.0.0.1:5000`, which is the default port for the backend if deployed locally. If you are running the frontend in a browser with the address bar showing `file://` instead of showing `http://`, you may need to disable CORS on your browser temporarily. Plugins are available on Chromium browsers to temporarily disable CORS.

## Notes on deployment on Linux + Apache

It is possible to deploy the frontend to an external web hosting service eg Amazon AWS EC2. Because the simplicity of the frontend, the steps involved are not difficult.

1. Ensure Apache is installed on your Linux system
2. Clone the repo
3. Set up the webpages; e.g. copy the `frontend` folder to `var/www/html`, which is the default location of Apache ht-docs.
4. Verify that the deployment works by visiting the website from a browser.
