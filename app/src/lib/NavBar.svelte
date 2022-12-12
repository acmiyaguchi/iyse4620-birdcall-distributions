<script>
  export let path = [];
  export let client_status;
</script>

<nav class="box">
  <div>
    <a href="/">home</a>
    {#each path as part, i}
      <a href={"/" + path.slice(0, i).join("/")}>{part}</a>
    {/each}
  </div>
  {#if client_status}
    <div>
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
  .box {
    display: flex;
    justify-content: space-between;
  }
</style>
