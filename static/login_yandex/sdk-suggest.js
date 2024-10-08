require('dotenv').config();

const apiKey = process.env.YANDEX_CLIENT_ID;
console.log(apiKey); // выводит ваш API ключ


YaAuthSuggest.init(
    {
       client_id: YANDEX,
       response_type: 'token',
       redirect_uri: 'https://examplesite.com/suggest/token'
    },
    'https://examplesite.com'
 )
 .then(({
    handler
 }) => handler())
 .then(data => console.log('Сообщение с токеном', data))
 .catch(error => console.log('Обработка ошибки', error));

//  <head>
//    <script src="https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-with-polyfills-latest.js"></script>
//    </head>