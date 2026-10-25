akesecn nandon rnsnGeC

Costof clustring of ClusterGCGCusteGC useste hihly optimized METIS software $\dagger\dagger$ to perform clustering. Table 9 summarizes the time to obtain the clusters for the five graphs. On the large and dense Amazon graph, the cost of clustering increase dramatically. The pre-processing time of ClusterGCN on Amazon is more than $4 \times$ of the total training time. On the other hand, the sampling cost of GraphSAINT does not increase significantly for large graphs (see Figure 7).

2aeCn inoeGSuguGeC

Taking into account the pre-processing time, sampling time and training time altogether, we summarize the total convergence time of GraphSAINT and ClusterGCN in Table 10 (corresponding to Table 2 configuration). On graphs that are large and dense (e.g., Amazon), GraphSAINT achieves significantly faster convergence. Note that both the sampling of GraphSAINT and clustering of ClusterGCN can be performed ofline

l CGonontaenetnenongscend

D.3 EFFECT OF BATCH SIZE
Table 11 shows the change of test set accuracy with batch sizes. For each row of Table 11, we fix the batch size, tune the other hyperparameters according to Appendix C.3, and report the highest test set accuracy achieved. For GraphSAGE, S-GCN and AS-GCN, their default batch sizes (512,1000 and 512, respectively) lead to the highest accuracy on all datasets. For FastGCN, increasing the default batch size (from 400 to 4000) leads to noticeable accuracy improvement. For ClusterGCN, different datasets correspond to different optimal batch sizes. Note that the accuracy in Section 5.1 is already tuned by identifying the optimal batch size on a per graph basis.

For FastGCN, intuitively, increasing batch size may help with accuracy improvement since the minibatches may become better connected. Such intuition is verified by the rows of 400 and 2000. However, increasing the batch size from 2000 to 4000 does not further improve accuracy significantly. For ClusterGCN, the optimal batch size depends on the cluster structure of the training graph. For PPI, small batches are better, while for Amazon, batch size does not have significant impact on accuracy. For GraphSAGE, overly large batches may have negative impact on accuracy due to 2hGe2812532 Anakcoand econo $1 0 \times$ wpeneiahor ndscronrne
 $2 \times1 0^{3}$ minibatch would then require the support of $2 \times1 0^{5}$ 
