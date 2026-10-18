FROM golang:1.24-alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

FROM alpine:3.20
RUN adduser -D app
USER app
COPY --from=build /app /app
EXPOSE 8080
CMD ["/app"]
