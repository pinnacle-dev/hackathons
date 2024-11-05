cd 21102024-ArXiv/web
export $(grep -v '^#' .env | xargs)
npm build
npm start
