FROM openresty/openresty:alpine

# Copy configuration files
COPY ./conf.d/transform.lua /etc/nginx/conf.d/transform.lua
COPY ./conf.d/default.conf /etc/nginx/conf.d/default.conf

# Verify the configuration
RUN nginx -t

# Set permissions
RUN chown -R nobody:nobody /etc/nginx/conf.d
