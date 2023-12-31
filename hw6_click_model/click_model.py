from collections import defaultdict
import math
import sys

from config import *

class BaseModel:
    def __init__(self, config=None):
        self.config = config if config is not None else {}
    
    def train(self, sessions):
        pass

    def test(self, testSessions):
        logLikelihood = 0.0
        positionPerplexity = [0.0] * self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY)
        positionPerplexityClickSkip = [[0.0, 0.0] \
                                       for i in range(self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY))]
        counts = [0] * self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY)
        countsClickSkip = [[0, 0] for i in range(self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY))]
        possibleIntents = [False]
        for s in testSessions:
            intentWeight = {False: 1.0}
            clickProbs = self._get_click_probs(s, possibleIntents)
            N = min(len(s.clicks), self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY))
            # P(C_1, ..., C_N) = \sum_{i} P(C_1, ..., C_N | I=i) P(I=i)
            logLikelihood += math.log(sum(clickProbs[i][N-1] * intentWeight[i] for i in possibleIntents)) / N
            correctedRank = 0
            for k, click in enumerate(s.clicks):
                click = 1 if click else 0
                # P(C_k | C_1, ..., C_{k-1}) = \sum_{I} P(C_1, ..., C_k | I) P(I) / \sum_{I} P(C_1, ..., C_{k-1} | I) P(I)
                curClick = dict((i, clickProbs[i][k]) for i in possibleIntents)
                prevClick = dict((i, clickProbs[i][k-1]) for i in possibleIntents) if k > 0 else dict(\
                    (i, 1.0) for i in possibleIntents)
                logProb = math.log(sum(curClick[i] * intentWeight[i] for i in possibleIntents), 2) - math.log(\
                    sum(prevClick[i] * intentWeight[i] for i in possibleIntents), 2)
                positionPerplexity[correctedRank] += logProb
                positionPerplexityClickSkip[correctedRank][click] += logProb
                counts[correctedRank] += 1
                countsClickSkip[correctedRank][click] += 1
                correctedRank += 1
        positionPerplexity = [2 ** (-x/count if count else x) for (x, count) in zip(positionPerplexity, counts)]
        positionPerplexityClickSkip = [[2 ** (-x[click] / (count[click] if count[click] else 1) if count else x) \
                                        for (x, count) in zip(positionPerplexityClickSkip, countsClickSkip)] for click in range(2)]
        perplexity = sum(positionPerplexity) / len(positionPerplexity)
        return logLikelihood / len(testSessions), perplexity, positionPerplexity, positionPerplexityClickSkip

    def _get_click_probs(self, s, possibleIntents):
        """
        returns click probabilities list for a given list of s.clicks
        for each intent i and each rank k, we have:
            click_probs[i][k-1] = P(C_1, ..., C_k | I=i)
        """
        click_probs = dict((i, [0.5 ** (k+1) for k in range(len(s.clicks))]) for i in possibleIntents)
        return click_probs

class ClickModel(BaseModel):
    
    def train(self, sessions):
        print("Click Model training...")
        max_query_id = self.config.get('MAX_QUERY_ID', MAX_QUERY_ID)
        possibleIntents = [False]
        # alpha: intent -> query -> result -> "attractiveness probability"
        self.alpha = dict((i, [defaultdict(lambda: self.config.get('DEFAULT_REL', DEFAULT_REL)) for q in range(max_query_id)]) for i in possibleIntents)
        # gamma: rank -> "examination probability"
        self.gamma = [0.5 for r in range(self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY))]
        # beta: query_id -> "reformulation probability"
        self.beta = [0.5 for q in range(max_query_id)]
        for iteration_cnt in range(self.config.get('MAX_ITERATIONS', MAX_ITERATIONS)):
            self.queryIntentsWeights = defaultdict(lambda:[])
            alphaFractions = dict((i, [defaultdict(lambda: list(self.config.get('ALPHA_PRIOR', ALPHA_PRIOR))) for q in range(max_query_id)]) for i in possibleIntents)
            gammaFractions = [[1.0, 2.0] for r in range(self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY))]
            betaFractions = [list(self.config.get('BETA_PRIOR', BETA_PRIOR)) for q in range(max_query_id)]
            
            # E-step
            for s in sessions:
                query = s.query
                alphaList, gammaList, betaList = self.get_session_para(s)
                f, b, z = self.get_forward_backward(s.clicks, alphaList, gammaList, betaList)

                for rank, (c, res) in enumerate(zip(s.clicks, s.results)):
                    f0 = 1.0 if rank == 0 else f[rank-1][0]
                    f1 = 0.0 if rank == 0 else f[rank-1][1]

                    # update gamma
                    if c == 1:
                        gammaFractions[rank][0] += 1.0
                        gammaFractions[rank][1] += 1.0
                    else:
                        p00 = f0 * b[rank][0] * (1.0 - gammaList[rank])
                        q10 = b[rank][0] * (1.0 - alphaList[rank] + alphaList[rank] * betaList[0]) * f0 * gammaList[rank]
                        q11 = b[rank][1] * alphaList[rank] * betaList[0] * f0 * gammaList[rank]
                        p10 = q10 + q11
                        p01 = f1 * b[rank][1]
                        z_p = p00 + p10 + p01
                        gammaFractions[rank][0] += p10 / z_p
                        gammaFractions[rank][1] += 1.0 - p01 / z_p
                    
                    # update alpha
                    if c == 1:
                        alphaFractions[False][query][s.results[rank]][0] += 1.0
                    else:
                        p1 = b[rank][0] * (1.0 - gammaList[rank] + gammaList[rank] * betaList[0])
                        p1 += b[rank][1] * gammaList[rank] * betaList[0]
                        p1 *= f0
                        p1 += b[rank][1] * f1
                        p1 *= alphaList[rank]
                        p1 /= z[rank]
                        alphaFractions[False][query][s.results[rank]][0] += p1
                    alphaFractions[False][query][s.results[rank]][1] += 1.0

                    # update beta
                    if c == 1:
                        betaFractions[query][0] += 1.0
                    else:
                        p1 = f0 * b[rank][0] * (1.0 - gammaList[rank] * alphaList[rank]) + f1 * b[rank][1]
                        p1 *= (1.0 - betaList[0])
                        p1 /= z[rank]
                        betaFractions[query][0] += p1
                    betaFractions[query][1] += 1.0
            
            # M-step
            sum_sqrl = 0.0
            # gamma
            for r in range(self.config.get('MAX_DOCS_PER_QUERY', MAX_DOCS_PER_QUERY)):
                gF = gammaFractions[r]
                new_gamma = gF[0] / gF[1]
                sum_sqrl += (self.gamma[r] - new_gamma) ** 2
                self.gamma[r] = new_gamma
            # alpha
            for i in possibleIntents:
                for q in range(max_query_id):
                    for res, aF in alphaFractions[i][q].items():
                        new_alpha = aF[0] / aF[1]
                        sum_sqrl += (self.alpha[i][q][res] - new_alpha) ** 2
                        self.alpha[i][q][res] = new_alpha
            # beta
            for q in range(max_query_id):
                new_beta = betaFractions[q][0] / betaFractions[q][1]
                sum_sqrl += (self.beta[q] - new_beta) ** 2
                self.beta[q] = new_beta

    def get_rel_para(self, query, res):
        return self.alpha[False][query][res], self.beta[query]

    def get_session_para(self, session):
        alphaList = []
        gammaList = []

        query = session.query
        for rank, res in enumerate(session.results):
            alphaList.append(self.alpha[False][query][res])
            gammaList.append(self.gamma[rank])
        betaList = [self.beta[query]]

        return alphaList, gammaList, betaList

    def get_forward_backward(self, clicks, alphaList, gammaList, betaList):
        M = len(clicks)
        f = [[1.0, 0]]
        b = [[1.0, 1.0] for i in range(M)]
        z = [1.0]
        
        # P(C_i = t|E_{i-1} = 1, C_{i-1} = 0) = p[i][t]
        p = []

        # forward
        for i, c in enumerate(clicks):
            t0 = 1 - gammaList[i]
            t0 += gammaList[i] * (1.0 - alphaList[i] + alphaList[i] * betaList[0])
            t1 = gammaList[i] * alphaList[i] * (1 - betaList[0])
            p.append([t0, t1])
            if c == 0:
                f.append([
                    f[i][0] * p[i][0],
                    f[i][0] * p[i][1] + f[i][1]
                ])
            else:
                f.append([
                    f[i][0] * p[i][0],
                    f[i][0] * p[i][1]
                ])
            
            z.append(sum(f[i+1]))
            f[i+1][0] /= z[i+1]
            f[i+1][1] /= z[i+1]
        
        f = f[1:]
        z = z[1:]

        # backward
        for i in range(M-2, -1, -1):
            if clicks[i+1] == 0:
                b[i][0] = b[i+1][0] * p[i+1][0] + b[i+1][1] * p[i+1][1]
                b[i][1] = b[i+1][1]
            else:
                b[i][0] = b[i+1][0] * p[i+1][0] + b[i+1][1] * p[i+1][1]
                b[i][1] = 0.0
            b[i] = [b[i][0] / z[i+1], b[i][1] / z[i+1]]
        
        return f, b, z

    def _get_click_probs(self, s, possibleIntents):
        alphaList, gammaList, betaList = self.get_session_para(s)
        f, b, z = self.get_forward_backward(s.clicks, alphaList, gammaList, betaList)
        clickProbs = []
        for i in range(len(z)):
            clickProbs.append(1.0 * z[i] if i == 0 else clickProbs[i-1] * z[i])
        return dict((i, clickProbs) for i in possibleIntents)