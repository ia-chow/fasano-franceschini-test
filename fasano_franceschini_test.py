# Ian Chow
# Multivariate generalization of the Kolmogorov-Smirnov test in Python, implemented according to the method outlined by Fasano & Franceschini (1987) and based on the R implementation by Puritz et al. (2023)
# References:
# 1. Peacock, J. A. (1983). Two-dimensional goodness-of-fit testing in astronomy. Monthly Notices of the Royal Astronomical Society, 202(3), 615-627.
# 2. Fasano, G., & Franceschini, A. (1987). A multidimensional version of the Kolmogorov–Smirnov test. Monthly Notices of the Royal Astronomical Society, 225(1), 155-170.
# 3. Puritz, C., Ness-Cohn, E. & Braun, R. (2023). fasano.franceschini.test: An Implementation of a Multivariate KS Test in R. The R Journal, 15(3), 159-171.
import numpy as np
import itertools

def ff_test_2sample(s1, s2):
    """
    Computes the 2-sample Fasano-Franceschini test, a multivariate generalization of the Kolmogorov-Smirnov test as outlined by Fasano & Franceschini (1987). The test evaluates the null hypothesis H0 that two i.i.d. random samples are drawn from the same underlying probability distribution. Although Fasano & Franceschini's original paper only evaluates two- and three-dimensional data, the test can be extended to arbitrary dimensions.

    :param array-like s1: n1 x d array of samples with length n1 and dimension d
    :param array-like s2: n2 x d array of samples with length n2 and dimension d

    :return: a tuple of the following values:

    float statistic: The value of the test statistic, Dn
    float p-value (NEED TO IMPLEMENT): The p-value
    """
    # lengths and dimensions of the two samples
    n1, dim1 = s1.shape
    n2, dim2 = s2.shape
    # if they don't have same number of dimensions raise an error
    if dim1 != dim2:
        raise TypeError('S1 and S2 do not have the same number of dimensions')
    # create permutation array for all permutations of (-1, 1) over all D dimensions (length 2^D)
    permarr = np.array(list(itertools.product(*[(1, -1) for d in range(dim1)])))
    # manipulate s1 and s2 arrays to get broadcastable arrays, permuting every sample into every orthant  
    s1_bc = (permarr[:, None] * s1)[None, :, :, :]  # broadcast array to broadcast
    s1_pt = (permarr * s1[:, None])[:, :, None, :]  # point array to be broadcast over
    s2_bc = (permarr[:, None] * s2)[None, :, :, :]
    s2_pt = (permarr * s2[:, None])[:, :, None, :]
    # Orthant probabilities for all orthants and all samples from 1...n1 and 1...n2
    # Compute the normalized probability of finding points in s1, s2 in each of the 2^d orthants of d-dimensional 
    # space for s1, s2 by counting the fraction of points in each volume and dividing by the sample size using 
    # numpy broadcasting for efficient vectorized operations
    normed_orth_probs_s11 = np.sum(np.bitwise_and.reduce(s1_bc > s1_pt, axis=-1), axis=-1)/n1
    normed_orth_probs_s21 = np.sum(np.bitwise_and.reduce(s2_bc > s1_pt, axis=-1), axis=-1)/n2
    normed_orth_probs_s12 = np.sum(np.bitwise_and.reduce(s1_bc > s2_pt, axis=-1), axis=-1)/n1
    normed_orth_probs_s22 = np.sum(np.bitwise_and.reduce(s2_bc > s2_pt, axis=-1), axis=-1)/n2
    # Compute the D1, D2 test statistics as the maximum distance between two corresponding orthant probabilities for 
    # s1 and s2 across all 2^D orthants and across all samples 1...n1 and 1...n2:
    D1 = np.max(np.abs(normed_orth_probs_s11 - normed_orth_probs_s21))
    D2 = np.max(np.abs(normed_orth_probs_s12 - normed_orth_probs_s22))
    # Compute test statistic as the average of the two D1, D2 statistics scaled by the sample size:
    Dn = np.sqrt((n1 * n2)/(n1 + n2)) * np.mean((D1, D2))
    # return test statistic Dn
    return Dn