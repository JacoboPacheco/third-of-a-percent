; Standalone module made from the IR dumps in raw/B-c18-kernels-none-ir.json (see extract.py).
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, ptr }

declare i64 @llvm.umax.i64(i64, i64)

; *** IR Dump Before LoopVectorizePass on _Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, inaccessiblemem: none) uwtable
define dso_local noundef i64 @_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0) local_unnamed_addr #0 {
entry:
  %2 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %3 = load ptr, ptr %2, align 8
  %4 = load ptr, ptr %0, align 8
  %5 = icmp eq ptr %3, %4
  br i1 %5, label %bb14, label %bb6

bb6:                                                ; preds = %entry
  %7 = ptrtoint ptr %3 to i64
  %8 = ptrtoint ptr %4 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = call i64 @llvm.umax.i64(i64 %10, i64 1)
  br label %bb16

bb12:                                               ; preds = %bb16
  %13 = phi i64 [ %22, %bb16 ]
  br label %bb14

bb14:                                               ; preds = %bb12, %entry
  %15 = phi i64 [ 0, %entry ], [ %13, %bb12 ]
  ret i64 %15

bb16:                                               ; preds = %bb6, %bb16
  %17 = phi i64 [ %23, %bb16 ], [ 0, %bb6 ]
  %18 = phi i64 [ %22, %bb16 ], [ 0, %bb6 ]
  %19 = getelementptr inbounds i32, ptr %4, i64 %17
  %20 = load i32, ptr %19, align 4
  %21 = sext i32 %20 to i64
  %22 = add nsw i64 %18, %21
  %23 = add nuw i64 %17, 1
  %24 = icmp eq i64 %23, %11
  br i1 %24, label %bb12, label %bb16
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_ ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) uwtable
define dso_local void @_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %2) local_unnamed_addr #1 {
entry:
  %4 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = load ptr, ptr %1, align 8
  %7 = icmp eq ptr %5, %6
  br i1 %7, label %bb17, label %bb8

bb8:                                                ; preds = %entry
  %9 = ptrtoint ptr %5 to i64
  %10 = ptrtoint ptr %6 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = load ptr, ptr %2, align 8
  %14 = load ptr, ptr %0, align 8
  %15 = call i64 @llvm.umax.i64(i64 %12, i64 1)
  br label %bb18

bb16:                                               ; preds = %bb18
  br label %bb17

bb17:                                               ; preds = %bb16, %entry
  ret void

bb18:                                               ; preds = %bb8, %bb18
  %19 = phi i64 [ 0, %bb8 ], [ %26, %bb18 ]
  %20 = getelementptr inbounds i32, ptr %6, i64 %19
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr inbounds i32, ptr %13, i64 %19
  %23 = load i32, ptr %22, align 4
  %24 = add nsw i32 %23, %21
  %25 = getelementptr inbounds i32, ptr %14, i64 %19
  store i32 %24, ptr %25, align 4
  %26 = add nuw i64 %19, 1
  %27 = icmp eq i64 %26, %15
  br i1 %27, label %bb16, label %bb18
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) uwtable
define dso_local void @_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = getelementptr i32, ptr %5, i64 -1
  %11 = icmp ugt i64 %9, 2
  br i1 %11, label %bb12, label %bb15

bb12:                                               ; preds = %entry
  %13 = load ptr, ptr %0, align 8
  br label %bb16

bb14:                                               ; preds = %bb16
  br label %bb15

bb15:                                               ; preds = %bb14, %entry
  ret void

bb16:                                               ; preds = %bb12, %bb16
  %17 = phi i64 [ 2, %bb12 ], [ %28, %bb16 ]
  %18 = phi i64 [ 1, %bb12 ], [ %17, %bb16 ]
  %19 = getelementptr i32, ptr %10, i64 %18
  %20 = load i32, ptr %19, align 4
  %21 = getelementptr inbounds i32, ptr %5, i64 %18
  %22 = load i32, ptr %21, align 4
  %23 = add nsw i32 %22, %20
  %24 = getelementptr inbounds i32, ptr %5, i64 %17
  %25 = load i32, ptr %24, align 4
  %26 = add nsw i32 %23, %25
  %27 = getelementptr inbounds i32, ptr %13, i64 %18
  store i32 %26, ptr %27, align 4
  %28 = add nuw i64 %17, 1
  %29 = icmp eq i64 %28, %9
  br i1 %29, label %bb14, label %bb16
}


; *** IR Dump Before LoopVectorizePass on _Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) uwtable
define dso_local void @_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds %"class.std::__1::vector", ptr %1, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb14, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %5 to i64
  %9 = ptrtoint ptr %4 to i64
  %10 = sub i64 %9, %8
  %11 = ashr exact i64 %10, 2
  %12 = load ptr, ptr %0, align 8
  br label %bb15

bb13:                                               ; preds = %bb15
  br label %bb14

bb14:                                               ; preds = %bb13, %entry
  ret void

bb15:                                               ; preds = %bb7, %bb15
  %16 = phi i64 [ %11, %bb7 ], [ %17, %bb15 ]
  %17 = add i64 %16, -1
  %18 = getelementptr inbounds i32, ptr %5, i64 %17
  %19 = load i32, ptr %18, align 4
  %20 = shl nsw i32 %19, 1
  %21 = getelementptr inbounds i32, ptr %12, i64 %17
  store i32 %20, ptr %21, align 4
  %22 = icmp eq i64 %17, 0
  br i1 %22, label %bb13, label %bb15
}


; *** IR Dump Before LoopVectorizePass on _Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) uwtable
define dso_local void @_Z16kern_k05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #1 {
entry:
  %3 = getelementptr inbounds %"class.std::__1::vector", ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb15, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %4 to i64
  %9 = ptrtoint ptr %5 to i64
  %10 = sub i64 %8, %9
  %11 = ashr exact i64 %10, 2
  %12 = load ptr, ptr %1, align 8
  %13 = call i64 @llvm.umax.i64(i64 %11, i64 1)
  br label %bb16

bb14:                                               ; preds = %bb16
  br label %bb15

bb15:                                               ; preds = %bb14, %entry
  ret void

bb16:                                               ; preds = %bb7, %bb16
  %17 = phi i64 [ 0, %bb7 ], [ %26, %bb16 ]
  %18 = shl i64 %17, 1
  %19 = getelementptr inbounds i32, ptr %12, i64 %18
  %20 = load i32, ptr %19, align 4
  %21 = or disjoint i64 %18, 1
  %22 = getelementptr inbounds i32, ptr %12, i64 %21
  %23 = load i32, ptr %22, align 4
  %24 = add nsw i32 %23, %20
  %25 = getelementptr inbounds i32, ptr %5, i64 %17
  store i32 %24, ptr %25, align 4
  %26 = add nuw i64 %17, 1
  %27 = icmp eq i64 %26, %13
  br i1 %27, label %bb14, label %bb16
}

attributes #0 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, inaccessiblemem: none) uwtable }
attributes #1 = { mustprogress nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) uwtable }
