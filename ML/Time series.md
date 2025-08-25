## 1. 
**Stochastic processes** $X(t)$

**Description**
$$X_t = f(X_{t-1}, X_{t-2}, ...) + g(Z_t, Z_{t-1}, ...)$$

- mean $\mu(t) = E[X(t)]$
- autocovariance $\gamma(t_1, t_2) = E[X(t_1) - \mu(t_1)(X(t_2) -  \mu(t_2))]$

**Stationarity**
Strictly stationary if distribution of $X(t_1), ..., X(t_k)$ is the same as the joint distribution $X(t_{1 + \tau}), ..., X(t_{k + \tau})$
$$\gamma(t) = E[(X(t_1) - \mu)(X(t_1 + t) - \mu)]$$ac.f. 
$$\rho(t) = \gamma(t)/\gamma(0)$$

**Properties of ACF**
If $X(t)$ with mean $\mu$, variance $\sigma^2$
$$\rho(t) = \gamma(t) / \gamma(0) = \gamma(t) / \sigma^2$$
- $\rho(0) = 1$
- $\rho(t) = \rho(-t)$
- $|\rho(t) \leq 1$
- The ac.f. does not uniquely identify the underlying model

**White noise**
$$Z_t \sim \mathcal{N(0, \sigma_Z^2)}$$
$$\gamma(k) = \textrm{Cov}(Z_t, Z_{t+k}) = \begin{cases} \sigma_Z^2, \ k = 0, \\ 0, \ k \neq 0\end{cases}$$

**Random walk**
$Z_t \sim \mathcal{N}(\mu, \sigma_Z^2)$
$$X_t = X_{t-1} + Z_t$$$X_0 = 0 \Rightarrow X_t = \sum_{i = 1}^t Z_i$. $E[X_t] = t_\mu$, $\textrm{Var}(X_t) = t \sigma_Z^2$ 

**MA process**
$Z_t \sim \mathcal{N}(0, \sigma_Z^2)$. $X_t$ is said to be a moving average process of order q, $MA(q)$, if
$$X_t = \beta_0 Z_t + \beta_1 Z_{t-1} + ... + \beta_q Z_{t-q}$$$$\textrm{Cov}(X_t, X_{t+k}) = \textrm{Cov} (\beta_0 Z_t + \beta_1 Z_{t-1} + ... + \beta_q Z_{t-q}, \  \beta_0 Z_{t +k} + ... + \beta_q Z_{t + k - q}) =$$
$$\begin{cases} 0, k > q \\ \sigma_Z^2 \sum_{i = 0}^{q - k} \beta_i \beta_{i+1}, 0 \leq k \leq q \\ \gamma(-k), k < 0 \end{cases}$$

**Invertibility**
$X_t$ is said to be invertible if the $Z_t$ can be expressed as a convergent sum of present and past values of $X_t$ in the form
$$ Z_t = \sum_{j = 0}^\infty \pi_j X_{t-j}, \ \sum_{j=0}^\infty |\pi_j| < \infty$$
$$ B^j X_t = X_{t-j}$$
$$X_t = (\beta_0 + \beta_1 B + ... + \beta_q B^q)Z_t = \theta(B) Z_t$$It can be shown that an $MA(q)$ process is invertible if the complex roots of $\theta(x) = 0$ lie outside the unit circle

**AR process**
$Z_t$, $\sigma_Z^2$. Autoregressive process of order $p$, $AR(p)$:
$$X_t = \alpha_1 X_{t-1} + ... + \alpha_p X_{t-p} + Z_t$$ $$(1 - \alpha_1 B - ... - \alpha_p B^p)X_t = Z_t $$
or 
$$X_t = (1 - \alpha_1 B - ... - \alpha_p B^p)^{-1}Z_t = (1 + \beta_1 B + \beta_2 B^2 + ...)^{-1} Z_t = f(B) Z_t$$
$$\gamma(k) = \sigma_Z^2 \sum_{i=0}^{\infty} \beta_i \beta_{i + k}$$