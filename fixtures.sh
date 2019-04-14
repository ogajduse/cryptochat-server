set -e
set -o pipefail

CURL_COMMAND="curl"
CRYPTOCHAT_SERVER_FQDN=localhost
CRYPTOCHAT_SERVER_PORT=8888
CRYPTOCHAT_SERVER_URLSTART="http://$CRYPTOCHAT_SERVER_FQDN:$CRYPTOCHAT_SERVER_PORT"

generate_post_data()
{
  cat <<EOF
{"chat_id": $CHAT_ID, "sender_id": $SENDER_ID, "message": "$MESSAGE"}
EOF
}

CRYPTOCHAT_SERVER_URL=$CRYPTOCHAT_SERVER_URLSTART/api/users
# insert user1
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data '{"user_id": 123, "public_key":"public_key_data"}' | jq .

# insert user2
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data '{"user_id": 123456, "public_key":"public_key_data2"}' | jq .

CRYPTOCHAT_SERVER_URL=$CRYPTOCHAT_SERVER_URLSTART/api/contacts
# insert contact1
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data '{"owner_id": 123, "user_id": 123456, "encrypted_alias": "USER2 in contacts of USER1"}' | jq .

# insert contact2
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data '{"owner_id": 123456, "user_id": 123, "encrypted_alias": "USER1 in contacts of USER2"}' | jq .

CHAT_INFO=$(mktemp)
CRYPTOCHAT_SERVER_URL=$CRYPTOCHAT_SERVER_URLSTART/api/chats
# insert chat1
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data '{"users": [123, 123456], "sym_key_enc_by_owners_pub_keys": ["pkenc_data", "pkenc_data2"]}' | tee $CHAT_INFO | jq .
CHAT_ID=$(jq '.chat_id' $CHAT_INFO)

CRYPTOCHAT_SERVER_URL=$CRYPTOCHAT_SERVER_URLSTART/api/message/new
# insert message
SENDER_ID=123
MESSAGE="Hi there!"
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data "$(generate_post_data)" | jq .

# insert message
SENDER_ID=123456
MESSAGE="Oh hi! I have some news for you!"
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data "$(generate_post_data)" | jq .

# insert message
SENDER_ID=123
MESSAGE="I am curious, tell me..."
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data "$(generate_post_data)" | jq .

# insert message
SENDER_ID=123456
MESSAGE="We are not real... :-("
$CURL_COMMAND $CRYPTOCHAT_SERVER_URL -X 'POST' --data "$(generate_post_data)" | jq .
