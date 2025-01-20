const path = require("path");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  entry: {
    background: "./src/background/index.ts",
    popup: "./src/popup/index.ts",
  },
  output: {
    filename: "[name].js",
    path: path.resolve(__dirname, "dist"),
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  plugins: [
    new CleanWebpackPlugin(),
    new CopyPlugin({
      patterns: [
        { from: "manifest.json" },
        { from: "src/popup/index.html", to: "popup.html" },
        { from: "icons", to: "icons" },
      ],
    }),
  ],
  // Important for Chrome extensions
  optimization: {
    // Don't minimize to make debugging easier
    minimize: false,
  },
};
