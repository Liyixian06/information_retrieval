import argparse
import heapq
from click_model import *
from input_reader import *
outdir = 'output/'
rel_func = lambda a, g, b : a*g*(1.0-b)

def ranking(top_n = 5):
    print('Ranking...')
    fin = open(outdir+'relevance_estimation.txt', 'r', encoding='gb18030')
    data = defaultdict(dict)
    ret = []
    gammas = clickModel.gamma
    for line in fin:
        line = line.rstrip().split('\t')
        query = line[1]
        results = line[2].replace("\"",'').replace("\'",'').replace(' ','').lstrip('[').rstrip(']').split(',')
        alphas = json.loads(line[3])
        beta = float(line[4])

        for i in range(5):
            data[query][results[i]] = rel_func(alphas[i], gammas[i], beta)
    for query in data:
        if top_n == -1:
            final_results = sorted(data[query].items(), key=lambda x: x[1], reverse=True)
        else:
            final_results = heapq.nlargest(top_n, data[query].items(), key=lambda x: x[1])
        ret.append((query, final_results))
    fin.close()
    return ret

if __name__ == '__main__':
    readInput = InputReader(MIN_DOCS_PER_QUERY, MAX_DOCS_PER_QUERY, discard_no_clicks=False)
    sessions = readInput(sys.stdin)
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as test_clicks_file:
            testSessions = readInput(test_clicks_file)
    else:
        testSessions = sessions
    
    print('Train sessions: %d, test sessions: %d' % (len(sessions), len(testSessions)))
    print('Number of train sessions with %d+ results shown:' % MAX_DOCS_PER_QUERY, len([s for s in sessions if len(s.results) > SERP_SIZE + 1]))

    id_to_query = {}
    id_to_result = {}
    with open(outdir+'query_id.txt', 'w', encoding='gb18030') as f:
        for q, id in readInput.query_to_id.items():
            query, region = q
            id_to_query[id] = q
            f.write('%s\t%s\t%d\n' % (query, region, id))
    with open(outdir+'result_id.txt', 'w', encoding='gb18030') as f:
        for res, id in readInput.result_to_id.items():
            id_to_result[id] = res
            f.write('%s\t%s\n' % (res, id))
    f.close()

    config = {
        'MAX_QUERY_ID': readInput.current_query_id + 1,
        'MAX_ITERATIONS': MAX_ITERATIONS,
        'MAX_DOCS_PER_QUERY': MAX_DOCS_PER_QUERY,
        'SERP_SIZE': SERP_SIZE,
        'DEFAULT_REL': DEFAULT_REL
    }

    fout_pred = open(outdir+'click_prediction.txt', 'w', encoding='gb18030')
    fout_rel = open(outdir+'relevance_estimation.txt', 'w', encoding='gb18030')
    fout_rank = open(outdir+'ranking_relevance.txt', 'w', encoding='gb18030')

    baseModel = BaseModel(config=config)
    baseModel.train(sessions)
    clickModel = ClickModel(config=config)
    clickModel.train(sessions)
    print('Training finished.')

    print("Baseline Model testing...")
    print('BaseModel:', file = fout_pred)
    for s in testSessions:
        _ll, _perplex, _posPer, _posPerClickSkip = baseModel.test([s])
        print('%s\t%f\t%f\t%s\t%s\t%s' % (s.id, _ll, _perplex, str(_posPer), str(_posPerClickSkip), str(s.clicks)), file = fout_pred)
    print('\n', file = fout_pred)

    print("Click Model testing...")
    print('ClickModel:', file = fout_pred)
    for s in testSessions:
        _ll, _perplex, _posPer, _posPerClickSkip = clickModel.test([s])
        print('%s\t%f\t%f\t%s\t%s\t%s' % (s.id, _ll, _perplex, str(_posPer), str(_posPerClickSkip), str(s.clicks)), file = fout_pred)

    for s in testSessions:
        alpha, beta, result = [], '', []
        for res in s.results:
            _a, _b = clickModel.get_rel_para(s.query, res)
            alpha.append(_a)
            beta = _b
            result.append(id_to_result[res])
        print('%s\t%s\t%s\t%s\t%s' % (s.id, id_to_query[s.query][0], str(result), str(alpha), str(beta)), file = fout_rel)
    
    fout_pred.close()
    fout_rel.close()

    ranking_ret = ranking(top_n=5)
    for row in ranking_ret:
        print(row, file = fout_rank)
    fout_rank.close()
    print('Testing finished.')