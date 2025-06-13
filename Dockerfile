# Use lightweight web server
FROM nginx:alpine

# Copy your static files into the NGINX public directory
COPY dist/ /usr/share/nginx/html

# Optional: remove default config and copy your own (if needed)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port (Render automatically uses PORT env var)
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]

