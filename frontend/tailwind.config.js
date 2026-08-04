/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        prashanth: {
          teal: '#0B7C80',
          darkTeal: '#075659',
          red: '#8A1F2D',
          gold: '#D4AF37',
        }
      }
    },
  },
  plugins: [],
}
