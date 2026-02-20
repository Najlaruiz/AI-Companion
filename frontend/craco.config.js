// craco.config.js
const path = require("path");
const fs = require("fs");
require("dotenv").config();

// Check if we're in development mode
const isDevServer = process.env.NODE_ENV !== "production";

// Environment variable overrides
const config = {
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
  https: process.env.HTTPS === "true", // set HTTPS=true in .env to enable HTTPS
  port: process.env.PORT || 3000,
  certPath: process.env.HTTPS_CERT || "./localhost+2.pem",
  keyPath: process.env.HTTPS_KEY || "./localhost+2-key.pem",
};

let WebpackHealthPlugin;
let setupHealthEndpoints;
let healthPluginInstance;

// Load health check modules only if enabled
if (config.enableHealthCheck) {
  try {
    WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
    setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
    healthPluginInstance = new WebpackHealthPlugin();
  } catch (err) {
    console.warn("Health check plugins not found or not used:", err.message);
  }
}

const webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    configure: (webpackConfig) => {
      // Reduce watched directories for performance
      webpackConfig.watchOptions = {
        ...webpackConfig.watchOptions,
        ignored: [
          "**/node_modules/**",
          "**/.git/**",
          "**/build/**",
          "**/dist/**",
          "**/coverage/**",
          "**/public/**",
        ],
      };

      // Add health check plugin if enabled
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }

      return webpackConfig;
    },
  },
  devServer: (devServerConfig) => {
    // Enable HTTPS with mkcert if requested
    if (config.https) {
      devServerConfig.https = {
        key: fs.readFileSync(path.resolve(__dirname, config.keyPath)),
        cert: fs.readFileSync(path.resolve(__dirname, config.certPath)),
      };
    }

    // Listen on all network interfaces for public access
    devServerConfig.host = "0.0.0.0";
    devServerConfig.port = config.port;
    devServerConfig.historyApiFallback = true; // SPA routing

    // Add health check endpoints if enabled
    if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
      const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

      devServerConfig.setupMiddlewares = (middlewares, devServer) => {
        if (originalSetupMiddlewares) {
          middlewares = originalSetupMiddlewares(middlewares, devServer);
        }

        setupHealthEndpoints(devServer, healthPluginInstance);

        return middlewares;
      };
    }

    return devServerConfig;
  },
};

module.exports = webpackConfig;