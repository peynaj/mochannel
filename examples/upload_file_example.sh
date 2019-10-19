curl -X POST \
  http://localhost:8000/post/new/ \
  -H 'Accept: */*' \
  -H 'Authorization: JWT your_jwt_token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Host: localhost:8000' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -H 'content-length: 503682' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F source_type=channel \
  -F source_id=6 \
  -F 'text=test file uploading' \
  -F file=@/C:/Users/najafi-p/Downloads/SamplePNGImage_500kbmb.png