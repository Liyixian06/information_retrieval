from collections import namedtuple
import json

SessionItem = namedtuple('SessionItem', ['id', 'query', 'results', 'clicks'])

class InputReader:
    def __init__(self, min_docs_per_query, max_docs_per_query,
                 discard_no_clicks):
        self.result_to_id = {}
        self.query_to_id = {}
        self.current_result_id = 1
        self.current_query_id = 1

        self.min_docs_per_query = min_docs_per_query
        self.max_docs_per_query = max_docs_per_query
        self.discard_no_clicks = discard_no_clicks

    def __call__(self, f):
        sessions = []
        for line in f:
            sessionid, query, region, results, clicks = line.rstrip().split('\t')
            results, clicks = map(json.loads, [results, clicks])
            results = results[:self.max_docs_per_query]
            resObserved = len(results)
            clicks = clicks[:resObserved]
            if resObserved < self.min_docs_per_query:
                continue
            if self.discard_no_clicks and not any(clicks):
                continue
            
            if (query, region) in self.query_to_id:
                query_id = self.query_to_id[(query, region)]
            else:
                query_id = self.current_query_id
                self.query_to_id[(query, region)] = self.current_query_id
                self.current_query_id += 1
            result_ids = []
            for res in results:
                if res in self.result_to_id:
                    result_ids.append(self.result_to_id[res])
                else:
                    res_id = self.current_result_id
                    result_ids.append(res_id)
                    self.result_to_id[res] = res_id
                    self.current_result_id += 1
            sessions.append(SessionItem(sessionid, query_id, result_ids, clicks))
        return sessions