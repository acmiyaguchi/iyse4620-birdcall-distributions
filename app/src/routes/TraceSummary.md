<script>
  import Table from "$lib/Table.svelte";
  export let trace = [];
  export let should_show = true;

  function show_significant(trace, should_show) {
    if (!should_show) {
      return trace;
    }
    // only keep elements that do not include 0 on their credible interval
    return trace.filter(
      (x) => (x["hdi_2.5%"] < 0 && x["hdi_97.5%"] < 0) || (x["hdi_2.5%"] > 0 && x["hdi_97.5%"] > 0)
    );
  }
</script>

{#if trace.length > 0}

### misc parameters

This table contains posterior estimates for hyper-parameters for the CAR distribution such as $\alpha$ and $\tau$, as well as the intercept and slope parameters $\beta$ for the linear regression.

<Table
  data={show_significant(
    trace.filter((x) => !x.index.includes("phi[") && !x.index.includes("mu[")),
    should_show
  )}
/>

Note that the land cover classification features often change from species to species.
We can infer types of habits or environmental preferences from the significant features in the model.

### spatial random effect $\phi$

This measures random spatial variation across grid cells.
The prior $\phi$ is drawn from the CAR distribution i.e. $\phi_i \sim CAR(\mu_i, \tau_i, \alpha, W)$.

<Table
  data={show_significant(
    trace.filter((x) => x.index.includes("phi[")),
    should_show
  )}
  paginationSize={10}
/>

Observe how the random effects are more significant in the simpler `intercept_car` model than in the more complex `intercept_car_spatial` model.

### poisson parameter $\mu$

The prior $\mu$ is the rate parameter, which controls the expected number of observations in each grid cell.
Note there are some notational inconsistencies here; this is the same as our $\theta$ parameter in the model definitions, and is properly known as $\lambda$ in the Poisson distribution.

<Table
  data={show_significant(
    trace.filter((x) => x.index.includes("mu[")),
    should_show
  )}
  paginationSize={10}
/>

{/if}
