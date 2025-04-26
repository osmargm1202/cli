#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DOCKER_IMAGE_NAME" ] || [ -z "$DOCKER_IMAGE_TAG" ] || [ -z "$DOCKER_SAVE_FILE" ]; then
    echo "Error: Required environment variables are not set in .env file"
    echo "Please set DOCKER_IMAGE_NAME, DOCKER_IMAGE_TAG, and DOCKER_SAVE_FILE"
    exit 1
fi

# Default tag is from .env, but can be overridden with -t
TAG="$DOCKER_IMAGE_TAG"

# Initialize flags
BUILD_FLAG=false
BUILD_NO_CACHE_FLAG=false
SAVE_FLAG=false
PUSH_FLAG=false
TAG_FLAG=false
CREATE_PROD_CONTEXT_FLAG=false
DEPLOY_PROD_FLAG=false
REMOVE_PROD_CONTEXT_FLAG=false

# Check command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <options>"
    echo "Options:"
    echo "  d     Build Docker image"
    echo "  c     Build Docker image with no cache"
    echo "  s     Save Docker image"
    echo "  p     Push Docker image to registry"
    echo "  t     Tag image as latest"
    echo "  cp    Create production Docker context"
    echo "  dp    Deploy to production context"
    echo "  rp    Remove production Docker context"
    echo ""
    echo "You can combine multiple options: ./build.sh d p t"
    exit 1
fi

# Process arguments
for arg in "$@"; do
    case $arg in
        d)
            BUILD_FLAG=true
            ;;
        c)
            BUILD_NO_CACHE_FLAG=true
            ;;
        s)  
            SAVE_FLAG=true
            ;;
        p)
            PUSH_FLAG=true
            ;;
        t)
            TAG_FLAG=true
            ;;
        cp)
            CREATE_PROD_CONTEXT_FLAG=true
            ;;
        dp)
            DEPLOY_PROD_FLAG=true
            ;;
        rp)
            REMOVE_PROD_CONTEXT_FLAG=true
            ;;
        *)
            echo "Invalid option: $arg"
            echo "Usage: $0 <options>"
            echo "Run without arguments to see help"
            exit 1
            ;;
    esac
done

# Execute operations in sequence
if [ "$BUILD_FLAG" = true ]; then
    echo "Building Docker image: $DOCKER_IMAGE_NAME:$TAG"
    docker build -t "$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG" .
fi

if [ "$BUILD_NO_CACHE_FLAG" = true ]; then
    echo "Building Docker image with no cache: $DOCKER_IMAGE_NAME:$TAG"
    docker build --no-cache -t "$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG" .
fi

if [ "$SAVE_FLAG" = true ]; then
    echo "Saving Docker image to: $DOCKER_FOLDER_SAVE/$DOCKER_SAVE_FILE"
    mkdir -p "$DOCKER_FOLDER_SAVE"
    docker save -o "$DOCKER_FOLDER_SAVE/$DOCKER_SAVE_FILE" "$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG"
fi

if [ "$PUSH_FLAG" = true ]; then
    echo "Pushing Docker image to registry: $DOCKER_URL/$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG"
    docker push "$DOCKER_URL/$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG"
fi

if [ "$TAG_FLAG" = true ]; then
    echo "Tagging Docker image: $DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG as $DOCKER_URL/$DOCKER_USER/$DOCKER_IMAGE_NAME:latest"
    docker tag "$DOCKER_USER/$DOCKER_IMAGE_NAME:$TAG" "$DOCKER_URL/$DOCKER_USER/$DOCKER_IMAGE_NAME:latest"
fi 

if [ "$CREATE_PROD_CONTEXT_FLAG" = true ]; then
    echo "Creating production Docker context"
    # Check if required environment variables are set
    if [ -z "$DOCKER_HOST_USER" ] || [ -z "$DOCKER_HOST_IP" ]; then
        echo "Error: Required environment variables for production context are not set"
        echo "Please set DOCKER_HOST_USER and DOCKER_HOST_IP in .env file"
        exit 1
    fi
    
    docker context create prod --docker "host=ssh://$DOCKER_HOST_USER@$DOCKER_HOST_IP"
    echo "Production context created successfully"
fi

if [ "$DEPLOY_PROD_FLAG" = true ]; then
    echo "Deploying to production context"
    
    echo "Deploying with docker-compose"

    # Pull the latest image before deploying
    docker --context prod pull "$DOCKER_URL/$DOCKER_USER/$DOCKER_IMAGE_NAME:latest"

    # Check if docker-compose is installed
    docker --context prod compose up -d --remove-orphans
        
    echo "Deployment completed successfully"
fi

if [ "$REMOVE_PROD_CONTEXT_FLAG" = true ]; then
    echo "Removing production Docker context"
    docker context rm prod
    echo "Production context removed successfully"
fi 