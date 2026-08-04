module.exports = {
  apps: [
    {
      name: 'ph-slm-backend',
      script: '/home/ubuntu/ph-callcenter-slm-app/start_backend.sh',
      cwd: '/home/ubuntu/ph-callcenter-slm-app',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        APP_ENV: 'production',
        PORT: '8000'
      }
    },
    {
      name: 'ph-slm-frontend',
      script: 'npm',
      args: 'run preview -- --host 0.0.0.0 --port 5173',
      cwd: '/home/ubuntu/ph-callcenter-slm-app/frontend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
        PORT: '5173'
      }
    }
  ]
};
