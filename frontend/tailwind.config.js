/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--bg-light)',
        surface: 'var(--bg-light)',
        'bg-dark': 'var(--bg-dark)',
        primary: 'var(--text-dark)',
        secondary: 'var(--text-muted)',
        accent: 'var(--primary)',
        success: '#16A34A',
        warning: '#D97706',
        danger: '#DC2626',
        border: 'var(--border)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        mono: ['"Fira Code"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
