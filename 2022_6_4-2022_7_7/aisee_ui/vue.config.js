const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: "./",
  devServer: {
    historyApiFallback: false,
  },
  chainWebpack(config) {
    config.plugin('mini-css-extract-plugin')
        .use(require('mini-css-extract-plugin'), [{
              filename: '[name].[contenthash].css',
              chunkFilename: '[id].[contenthash].css'
          }]).end()
  },
  pages: {
    index: {
      entry: "src/main.js",
    },
    newsviewer: {
      entry: "src/newsViewer.js",
    },
    ocr:{
      entry: "src/OCRViewer.js",
    },
    favorite:{
      entry: "src/favoriteViewer.js",
    }
  },
});
