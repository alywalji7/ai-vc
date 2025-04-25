/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef5ff',
          100: '#d9e7ff',
          200: '#bcdbff',
          300: '#8fc0ff',
          400: '#5d9cff',
          500: '#3a76ff',
          600: '#1f55f7',
          700: '#1641e3',
          800: '#1838b8',
          900: '#1b3790',
          950: '#142156',
        },
        secondary: {
          50: '#edfcff',
          100: '#d6f6fc',
          200: '#b5eefa',
          300: '#83e3f6',
          400: '#48cded',
          500: '#25b0d8',
          600: '#1991b8',
          700: '#197595',
          800: '#1c5f7a',
          900: '#1c4f67',
          950: '#0d3446',
        },
        accent: {
          50: '#f2f9fd',
          100: '#e4f0fa',
          200: '#c2e3f5',
          300: '#8ccded',
          400: '#4db3e2',
          500: '#2498d0',
          600: '#1a7db2',
          700: '#186791',
          800: '#195677',
          900: '#194863',
          950: '#112f42',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.gray.700'),
            a: {
              color: theme('colors.primary.600'),
              '&:hover': {
                color: theme('colors.primary.700'),
              },
            },
            h1: {
              color: theme('colors.gray.900'),
            },
            h2: {
              color: theme('colors.gray.900'),
            },
            h3: {
              color: theme('colors.gray.900'),
            },
            h4: {
              color: theme('colors.gray.900'),
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
      }),
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'fade-in-down': 'fadeInDown 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        fadeInUp: {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: 0, transform: 'translateY(-20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        subtle: '0 2px 15px 0 rgba(0, 0, 0, 0.05)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
};