# X Platform configuration

Open the add-on through Home Assistant ingress. The launcher lets you choose the
platform Console or any running application. Applications bind to `0.0.0.0`
and are opened through the configured Home Assistant LAN host/IP and their
assigned port, such as `http://10.0.0.2:5173`.

1. Open **Settings** and save a GitHub token if private repositories are needed.
2. Open **Plugin catalog** to install Popcorn, or open **Repositories** for a
   custom Node.js project.
3. Set a unique port and the project's install/build/start commands.
4. Add repository-specific environment values under the repository card.
5. Use **Applications** to manage the process and inspect its logs.

The built-in X Installer runs at startup and every configured interval. After a
new Home Assistant custom integration is installed, Home Assistant may require
a restart before the integration becomes available.
