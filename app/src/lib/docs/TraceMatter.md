One key component of Bayesian analysis is the ability to quantify uncertainty in the model predictions.
We do this by sampling from the posterior distribution of the model parameters.
These samples form a trace.
We can summarize these traces into credible intervals, which describes how often a sample falls within a particular range.

We take advantage of this uncertainty to classify whether a particular parameter in the model is significant.
We say that a parameter in the model is significant if it's credible interval does not include zero (i.e. an analogy to rejecting the null hypothesis in a frequentist analysis).
