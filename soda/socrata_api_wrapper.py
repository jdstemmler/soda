import urllib2 as urllib
import datetime
import pandas as pd
import io
import pprint


class TokenError(Exception):
    pass


class SODA(object):
    """Socrata Open Data API Object"""

    def __init__(self, api_url, token=None, query=None, **kwargs):
        """Initialize the SODA object.

        INPUTS
            api_url: (string) the url of the API endpoint.
            token:   (string) your application token
            query:   (dict)   dictionary containing your query
            kwargs:  any other keyword argument for your query
        """

        self.api_url = api_url
        self.url = None
        self.token = token
        self.query = query

        if self.query is None:
            self.query = {}
        self.query.update(kwargs)

        if self.token is not None:
            self._parse_query()

    def set_query(self, query=None, **kwargs):
        """Set the API query if you haven't already"""

        self.query = query
        if self.query is None:
            self.query = {}
        self.query.update(kwargs)
        self._parse_query()

    def print_query(self):
        """Print out your query"""

        pprint.pprint(self.query)

    def set_token(self, token):
        """Set the token if you haven't already"""

        self.token = token
        self._parse_query()

    def _format_string(self, q):
        """Format the string for the web"""

        return urllib.quote(q, safe='=>:?$&/')

    def _parse_query(self):
        """Parse the query dictionary"""

        if self.token is None:
            raise TokenError("Please set your token! (use .set_token(token))")

        querylist = []
        for k, v in self.query.iteritems():
            querylist.append("&${k}={v}".format(k=k, v=v))

        q = "{apiurl}?$$app_token={token}".format(apiurl=self.api_url,
                                                  token=self.token)
        q += ''.join(querylist)

        self.url = self._format_string(q)

    def get_request(self):
        """Send the query to the API endpoint and get the raw data"""

        if self.token is None:
            raise TokenError("Please set your token! (use .set_token(token))")

        if self.query is None:
            print "No query is defined. Here comes all the data... "

        request = urllib.urlopen(self.url).read()
        return request

    def get_df(self):
        """Get the data as a pandas DataFrame"""

        if self.api_url.endswith('.json'):
            return pd.read_json(self.get_request())
        elif self.api_url.endswith('.csv'):
            return pd.read_csv(io.BytesIO(self.get_request()))
        else:
            print "API Endpoint type not understood. Returning None"
            return None

if __name__ == "__main__":

    # from settings import APP_TOKEN

    today = datetime.date.today()
    td = today.strftime('%Y-%m-%dT%H:%M:%S')

    # token = APP_TOKEN
    token = 'abcd1234'
    api_url = 'https://data.seattle.gov/resource/3k2p-39jp.json'
    query = dict(limit=10,
                 where="event_clearance_date >= '{}'".format(td)
                 )

    data = SODA(api_url, token=token, query=query)

    df = data.get_df()
    print df
