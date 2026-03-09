# Node.js Server Add-on Documentation

This document explains configuration and internal behavior of the
add-on.

------------------------------------------------------------------------

## Purpose

The add-on allows Home Assistant users to run custom Node.js services
without maintaining a separate server.

Projects are downloaded from GitHub and executed automatically.

------------------------------------------------------------------------

## Startup Process

When the add-on starts:

1.  GitHub repositories are downloaded
2.  Dependencies are installed using npm
3.  index.js is executed
4.  The process is monitored
5.  If it crashes, it restarts automatically

------------------------------------------------------------------------

## Repository Requirements

Each repository should contain:

index.js package.json

index.js acts as the entry point.

------------------------------------------------------------------------

## Example Project Structure

index.js package.json

Optional:

/src /modules /services /config

------------------------------------------------------------------------

## Environment Variables

Defined in add-on configuration.

Format:

NAME=VALUE

Example:

PORT=3000 DISCORD_TOKEN=xxxxx API_KEY=xxxxx

Usage:

``` js
process.env.PORT
```

These are typically used for:

-   API keys
-   authentication tokens
-   runtime configuration

------------------------------------------------------------------------

## Private Repositories

To use private repositories you must create a GitHub token.

https://github.com/settings/tokens

Settings required:

Personal access tokens (classic) repo permission enabled

------------------------------------------------------------------------

## Troubleshooting

Server does not start:

-   check index.js exists
-   check package.json exists
-   check dependency installation

Repository download fails:

-   verify token
-   verify repository format
