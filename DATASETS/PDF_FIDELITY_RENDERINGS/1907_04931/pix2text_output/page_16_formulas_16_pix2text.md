acecrnocncGeaGanrforonc3

2aelCniangonanonoeanr Eue Cedio

Coniuraion f Graptn T oreroue abe esuls is shon in ale . Configraion of GraphSAINT to eproduce Tabe 3results is shown in Table 6.

eowowedesrit teconigraionfo Figur $4$ 
 $L$ 海海海科出业 additional final layer that aggregates all the output hidden features of graph convolutional layers 1 to $x_{\mathrm{J K}}$ M tathaial .theaditional agegtion ayeroutus te final medding

\boldsymbol{x}_{\mathrm{J K}}=\sigma\left( \boldsymbol{W}_{\mathrm{J K}}^{\mathsf{T}} \cdot\bigoplus_{\ell=1}^{L} \boldsymbol{x}_{v}^{( \ell)} \right)

(7
weabas n L010 ecerenen-congcncanaton orL.M ehicieic hiv er 97 asdagcgaion.

feues popagat olayer $( \ell)$ heaphatenonof G Ciki a 201 alalates te edeweightsforneighbor $( \ell-1 )$ aggregation by an additional neural network. With multi-head  $( K )$ attention, the layer-
as follows:

\boldsymbol{x}_{v}^{( \ell)}=\Bigg\|_{k=1}^{K} \sigma\left( \sum_{u \in\mathrm{n e i g h b o r} ( v )} \alpha_{u , v}^{k} \boldsymbol{W}^{k} \boldsymbol{x}_{v}^{( \ell-1 )} \right)

(8)
where $| |$ isthe vectorconcataton peainan t cefient $\alpha$ is alulted ih the atenton weights $a^{k}$ by:

\alpha_{u , v}^{k}=\mathrm{L e a k y R e L U} \left( \left( \boldsymbol{a}^{k} \right)^{\mathsf{T}} \left[ \boldsymbol{W}^{k} \boldsymbol{x}_{u} \| \boldsymbol{W}^{k} \boldsymbol{x}_{v} \right] \right)

(9
Nte that the $\alpha$ calculationis slsgstl ifret ftom th rginl suation n Velitkovi er al. .017). Namely, GAT-SAINT does not normalize $\alpha$ by softmax across all neighbors of $v$ . We make such modification since under the minibatch setting, node $v$ does not see all its neighbors in the training graph. The removal of softmax is also seen in the attention design of Huang et al. (2018). Note that during the minibatch training, GAT-SAINT further applies another edge coefficient on top of attention for aggregator normalization.

ae anwsteonanontrGr n G ur inFigue $4$ 