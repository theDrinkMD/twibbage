from twilio.rest import Client

account_sid = "AC94e244a7e30d1c48d5f897c076244c0e"
auth_token = "9fb9e58839a87165533c62bc3b18d90d"
client = Client(account_sid, auth_token)

message = client.messages.create(
        "+16106083377",
        body="Jenny please?! I love you <3",
        from_="+12566678942")

print(message.sid)
