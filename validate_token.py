class ValidateToken(Resource):

    def get(self, account_token):
        
        with Database() as db:
            # the user that this token is bound to
            bound_user = None

            for user, token_data in db.dict["temp_account_tokens"].items():
                if token_data["token"] == account_token:

                    # get the user that this token is bound to
                    bound_user = user

                    # if the token is expired
                    is_expired = token_data["expiration"] < time.time()

            if bound_user is None:
                response = make_response("no account linked to token", 404)
                response.headers["Response-Type"] = "validate_token"

                return response

            if is_expired:
                response = make_response("no account linked to token", 404)
                response.headers["Response-Type"] = "validate_token"

                return response

            response = make_response({"validated_token": account_token, "validated_user_id": bound_user}, 200)
            response.headers["Response-Type"] = "validate_token"

            return response