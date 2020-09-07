# This file handles the retrieval of twitter posts requested by __main__.py
import tweepy  # Tweepy is the wrapper used to interact with twitter

# Authenticate Twitter client
auth = tweepy.OAuthHandler("LPE0k1GUiNFgVyai6W7LUh3Z1",
                           "692wgvElUMca3FZadC3bSDRHLo627mI1LPJBv2Vzsv2fMW5bGu")
auth.set_access_token("2956830581-3LXAvWWC7GjXFkdwemPFXKKw2KsumpcRxg8mnEm",
                      "SPDyU2nUS3zKKz6gm5sDanXTmEYSrgegUBdhMSEjoODj6")

# Create API object (used to communicate with API)
api = tweepy.API(auth)  # the api is connected using the provided auth

# The below class represents an object used for collecting tweets

class twitter():
    def __init__(self):  # The constructer for the class
      print()  # <-- this is a placeholder
    def search_keyword(self, keyword):
