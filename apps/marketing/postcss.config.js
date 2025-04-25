module.exports = {
  plugins: {
    'tailwindcss': {},
    'autoprefixer': {},
    ...(process.env.NODE_ENV === 'production'
      ? {
          '@fullhuman/postcss-purgecss': {
            content: [
              './src/pages/**/*.{js,ts,jsx,tsx}',
              './src/components/**/*.{js,ts,jsx,tsx}',
            ],
            defaultExtractor: (content) => content.match(/[\w-/:]+(?<!:)/g) || [],
            safelist: {
              standard: ['html', 'body'],
              deep: [/^bg-/, /^text-/, /^border-/, /^hover:/, /^focus:/, /^animate-/],
            },
          },
          'cssnano': {
            preset: 'default',
          },
        }
      : {}),
  },
};