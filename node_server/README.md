[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[![Buy me a coffee][buymeacoffee-shield]](https://www.buymeacoffee.com/extaas)


# Node.js Server Add-on for Home Assistant

This add-on provides a Node.js runtime environment inside Home Assistant
so you can run custom backend services directly from GitHub
repositories.

Typical use cases:
- Discord bots
- Telegram bots
- API services
- Webhook handlers
- MQTT utilities
- Custom automation backends

The add-on downloads repositories, installs dependencies, and runs the
Node.js server automatically.

------------------------------------------------------------------------

## Key Features

-   Run Node.js applications inside Home Assistant
-   Support for multiple GitHub repositories
-   Private repository access via GitHub token
-   Environment variable support
-   Automatic restart if a server crashes
-   Simple project structure

------------------------------------------------------------------------

## Basic Project Example

Repository structure:

index.js package.json

Example index.js

``` js
console.log("Server started")
```

Example package.json

``` json
{
  "name": "example-server",
  "version": "1.0.0",
  "main": "index.js"
}
```

------------------------------------------------------------------------

## Using Modules

Example file:

/folder/demo.js

``` js
console.log("Hello world")
```

Import:

``` js
import "./folder/demo.js"
```

Exporting function:

``` js
export function demo(){
  console.log("Hello world")
}
```

Usage:

``` js
import { demo } from "./folder/demo.js"
demo()
```

------------------------------------------------------------------------

## GitHub Token

Create token here: https://github.com/settings/tokens

Use: Personal access tokens (classic)

Enable permission: repo

This grants access to private repositories.

Recommended: set expiration to **No expiration** so services do not
suddenly stop.

------------------------------------------------------------------------

## Repository Format

USERNAME/REPOSITORY.git

Example: myUser/discord-bot.git

------------------------------------------------------------------------

## Environment Variables

Format:

NAME=VALUE

Example:

DISCORD_TOKEN=token_here PORT=3000 API_KEY=secret

Usage in Node.js:

``` js
process.env.DISCORD_TOKEN
```

------------------------------------------------------------------------

## Security

Never commit: - tokens - passwords - API keys

Use environment variables instead.
