module.exports = {
  plugins: {
    'tailwindcss': {},
    'autoprefixer': {},
    'postcss-flexbugs-fixes': {},
    ...(process.env.NODE_ENV === 'production'
      ? {
          'cssnano': {
            preset: ['default', {
              discardComments: {
                removeAll: true,
              },
              minifyFontValues: {
                removeQuotes: false,
              },
            }],
          },
          '@fullhuman/postcss-purgecss': {
            content: [
              './src/pages/**/*.{js,jsx,ts,tsx}',
              './src/components/**/*.{js,jsx,ts,tsx}',
            ],
            defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
            safelist: {
              standard: ['html', 'body', /^bg-/, /^text-/, /^border-/, /^hover:/, /^focus:/, /^active:/],
              deep: [/^prose/, /^modal/, /^form/],
              greedy: [/^react-/],
            },
          },
        }
      : {}),
  },
};