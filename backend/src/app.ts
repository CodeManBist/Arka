import express from 'express';
import repositoriesRoutes from './routes/repositories.routes.ts';

const app = express();

app.use(express.json());

app.use('/api/repositories', repositoriesRoutes);

export default app;