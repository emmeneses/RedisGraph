/*
* Copyright 2018-2021 Redis Labs Ltd. and Contributors
*
* This file is available under the Redis Labs Source Available License Agreement
*/

#include "RG.h"
#include "rg_matrix.h"

GrB_Info RG_eWiseAdd                // C = A + B
(
    RG_Matrix C,                    // input/output matrix for results
    const GrB_Semiring semiring,    // defines '+' for T=A+B
    const RG_Matrix A,              // first input:  matrix A
    const RG_Matrix B               // second input: matrix B
) {
	ASSERT(A != NULL);
	ASSERT(B != NULL);
	ASSERT(C != NULL);
	ASSERT(semiring != NULL);

	GrB_Info        info;
	GrB_Index       nrows;
	GrB_Index       ncols;
	GrB_Index       DM_nvals;
	GrB_Index       DP_nvals;

	GrB_Matrix      _A    =  NULL;
	GrB_Matrix      _B    =  NULL;
	GrB_Matrix      _C    =  RG_MATRIX_M(C);
	GrB_Matrix      AM    =  RG_MATRIX_M(A);
	GrB_Matrix      BM    =  RG_MATRIX_M(B);
	GrB_Matrix      ADP   =  RG_MATRIX_DELTA_PLUS(A);
	GrB_Matrix      ADM   =  RG_MATRIX_DELTA_MINUS(A);
	GrB_Matrix      BDP   =  RG_MATRIX_DELTA_PLUS(B);
	GrB_Matrix      BDM   =  RG_MATRIX_DELTA_MINUS(B);

	// TODO: check A, B and C are compatible

	RG_Matrix_DP_nvals(&DP_nvals, A);
	RG_Matrix_DM_nvals(&DM_nvals, A);
	if(DM_nvals > 0 || DP_nvals > 0) {
		info = RG_Matrix_export(&_A, A);
		ASSERT(info == GrB_SUCCESS);
	} else {
		_A = AM;
	}

	RG_Matrix_DP_nvals(&DP_nvals, B);
	RG_Matrix_DM_nvals(&DM_nvals, B);
	if(DM_nvals > 0 || DP_nvals > 0) {
		info = RG_Matrix_export(&_B, B);
		ASSERT(info == GrB_SUCCESS);
	} else {
		_B = BM;
	}

	//--------------------------------------------------------------------------
	// C = A + B
	//--------------------------------------------------------------------------

	info = GrB_Matrix_eWiseAdd_Semiring(_C, NULL, NULL, semiring, _A, _B, NULL);
	ASSERT(info == GrB_SUCCESS);

	// zero nvals
	RG_Matrix_setDPNvals(C, 0);
	RG_Matrix_setDMNvals(C, 0);

	if(_A != AM) GrB_free(&_A);
	if(_B != BM) GrB_free(&_B);

	return info;
}

