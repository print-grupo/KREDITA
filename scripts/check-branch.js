
const { execSync } = require('child_process');

try {
  // Pega o nome da branch atual
  const branchName = execSync('git rev-parse --abbrev-ref HEAD').toString().trim();

  // Regex aceita: main, develop, ou tipo/nome
  const regex = /^(main|develop|(feat|feature|fix|hotfix|docs|refactor|chore|test|release)\/[a-z0-9._-]+)$/;

  if (!regex.test(branchName)) {
    console.error('\n❌ [ERRO] Nome de branch fora do padrão: ' + branchName);
    console.error('👉 Exemplos permitidos:');
    console.error('   - feat/nome-da-tarefa');
    console.error('   - fix/nome-do-bug');
    console.error('   - docs/atualiza-readme');
    console.error('   - release/1.0.0');
    console.error('   - main ou develop\n');
    process.exit(1);
  }
} catch (error) {
  // Se não conseguir ler o nome da branch, permite passar para não travar
  process.exit(0);
}