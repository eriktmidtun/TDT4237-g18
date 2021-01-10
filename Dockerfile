# Webserver running nginx
FROM nginx:perl

# Import groupid environment variable
ENV GROUPID=${GROUPID}
ENV PORT_PREFIX=${PORT_PREFIX}

# Copy nginx config to the container
COPY nginx.conf /etc/nginx/nginx.conf