import { Router } from 'express';
import { cloneRepositoryController } from '../controllers/repositories.controller.ts';

const router = Router();

router.post('/clone', cloneRepositoryController);

export default router;