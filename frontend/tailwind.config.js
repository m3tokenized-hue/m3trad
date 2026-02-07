/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        heading: ['IBM Plex Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        background: '#050505',
        foreground: '#FAFAFA',
        surface: '#0A0A0A',
        'surface-highlight': '#171717',
        card: {
          DEFAULT: '#0A0A0A',
          foreground: '#FAFAFA'
        },
        popover: {
          DEFAULT: '#0A0A0A',
          foreground: '#FAFAFA'
        },
        primary: {
          DEFAULT: '#4F46E5',
          foreground: '#FFFFFF'
        },
        secondary: {
          DEFAULT: '#27272A',
          foreground: '#FAFAFA'
        },
        muted: {
          DEFAULT: '#171717',
          foreground: '#A1A1AA'
        },
        accent: {
          DEFAULT: '#F43F5E',
          foreground: '#FFFFFF'
        },
        destructive: {
          DEFAULT: '#7F1D1D',
          foreground: '#FEF2F2'
        },
        border: '#262626',
        input: '#262626',
        ring: '#4F46E5',
        chart: {
          '1': '#4F46E5',
          '2': '#F43F5E',
          '3': '#22C55E',
          '4': '#F59E0B',
          '5': '#8B5CF6'
        }
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem'
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
};
