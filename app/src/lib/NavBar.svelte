<script>
  // export let path = [];
  export let client_status;
</script>

<nav class="box">
  <div>
    <a href="/">[ home ]</a>
    <a href="/earth-engine">[ earth engine ]</a>
    <a href="https://github.com/acmiyaguchi/iyse6420-birdcall-distributions">[ github ]</a>
  </div>
  {#if client_status}
    <div class="box">
      <div>
        <b>git rev</b>:
        <a
          href="https://github.com/acmiyaguchi/iyse6420-birdcall-distributions/commit/{client_status.git_sha}"
          >{client_status.git_sha}</a
        >
        <b>app</b>: v{client_status.version}
      </div>
    </div>
  {/if}
</nav>

<style>
  a {
    text-decoration: none;
  }
  .box {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
  }
</style>
