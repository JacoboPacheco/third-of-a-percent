; Standalone module made from the IR dumps in raw/B-c20-variants-fast-ir.json (see extract.py).
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%"class.std::__1::vector" = type { ptr, ptr, ptr }

declare void @llvm.trap() #9999
declare i64 @llvm.umax.i64(i64, i64)
declare i32 @__gxx_personality_v0(...)

; *** IR Dump Before LoopVectorizePass on _Z9v_rev_preRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z9v_rev_preRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %10 = load ptr, ptr %9, align 8
  %11 = load ptr, ptr %0, align 8
  %12 = ptrtoint ptr %10 to i64
  %13 = ptrtoint ptr %11 to i64
  %14 = sub i64 %12, %13
  %15 = icmp ult i64 %14, %8
  br i1 %15, label %bb20, label %bb16

bb16:                                               ; preds = %entry
  %17 = icmp eq ptr %4, %5
  br i1 %17, label %bb22, label %bb18

bb18:                                               ; preds = %bb16
  %19 = ashr exact i64 %8, 2
  br label %bb23

bb20:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb21:                                               ; preds = %bb23
  br label %bb22

bb22:                                               ; preds = %bb21, %bb16
  ret void

bb23:                                               ; preds = %bb18, %bb23
  %24 = phi i64 [ %25, %bb23 ], [ %19, %bb18 ]
  %25 = add i64 %24, -1
  %26 = getelementptr inbounds nuw i32, ptr %5, i64 %25
  %27 = load i32, ptr %26, align 4
  %28 = shl nsw i32 %27, 1
  %29 = getelementptr inbounds nuw i32, ptr %11, i64 %25
  store i32 %28, ptr %29, align 4
  %30 = icmp eq i64 %25, 0
  br i1 %30, label %bb21, label %bb23
}


; *** IR Dump Before LoopVectorizePass on _Z10v_rev_spanRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z10v_rev_spanRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = load ptr, ptr %0, align 8
  %11 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %12 = load ptr, ptr %11, align 8
  %13 = ptrtoint ptr %12 to i64
  %14 = ptrtoint ptr %10 to i64
  %15 = sub i64 %13, %14
  %16 = icmp ugt i64 %8, %15
  br i1 %16, label %bb17, label %bb18

bb17:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb18:                                               ; preds = %entry
  %19 = icmp eq ptr %4, %5
  %20 = icmp ne ptr %10, null
  %21 = or i1 %19, %20
  br i1 %21, label %bb22, label %bb24

bb22:                                               ; preds = %bb18
  br i1 %19, label %bb26, label %bb23

bb23:                                               ; preds = %bb22
  br label %bb27

bb24:                                               ; preds = %bb18
  tail call void @llvm.trap()
  unreachable

bb25:                                               ; preds = %bb27
  br label %bb26

bb26:                                               ; preds = %bb25, %bb22
  ret void

bb27:                                               ; preds = %bb23, %bb27
  %28 = phi i64 [ %29, %bb27 ], [ %9, %bb23 ]
  %29 = add i64 %28, -1
  %30 = getelementptr inbounds nuw i32, ptr %5, i64 %29
  %31 = load i32, ptr %30, align 4
  %32 = shl nsw i32 %31, 1
  %33 = getelementptr inbounds nuw i32, ptr %10, i64 %29
  store i32 %32, ptr %33, align 4
  %34 = icmp eq i64 %29, 0
  br i1 %34, label %bb25, label %bb27
}


; *** IR Dump Before LoopVectorizePass on _Z9v_rev_rawRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z9v_rev_rawRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %10 = load ptr, ptr %9, align 8
  %11 = load ptr, ptr %0, align 8
  %12 = ptrtoint ptr %10 to i64
  %13 = ptrtoint ptr %11 to i64
  %14 = sub i64 %12, %13
  %15 = icmp ult i64 %14, %8
  br i1 %15, label %bb20, label %bb16

bb16:                                               ; preds = %entry
  %17 = icmp eq ptr %4, %5
  br i1 %17, label %bb22, label %bb18

bb18:                                               ; preds = %bb16
  %19 = ashr exact i64 %8, 2
  br label %bb23

bb20:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb21:                                               ; preds = %bb23
  br label %bb22

bb22:                                               ; preds = %bb21, %bb16
  ret void

bb23:                                               ; preds = %bb18, %bb23
  %24 = phi i64 [ %25, %bb23 ], [ %19, %bb18 ]
  %25 = add i64 %24, -1
  %26 = getelementptr inbounds nuw i32, ptr %5, i64 %25
  %27 = load i32, ptr %26, align 4
  %28 = shl nsw i32 %27, 1
  %29 = getelementptr inbounds nuw i32, ptr %11, i64 %25
  store i32 %28, ptr %29, align 4
  %30 = icmp eq i64 %25, 0
  br i1 %30, label %bb21, label %bb23
}


; *** IR Dump Before LoopVectorizePass on _Z9v_rev_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z9v_rev_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb21, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %4 to i64
  %9 = ptrtoint ptr %5 to i64
  %10 = sub i64 %8, %9
  %11 = ashr exact i64 %10, 2
  %12 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %0, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %11, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb26
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb7, %bb26
  %23 = phi i64 [ 0, %bb7 ], [ %31, %bb26 ]
  %24 = icmp eq i64 %23, %18
  br i1 %24, label %bb25, label %bb26

bb25:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb26:                                               ; preds = %bb22
  %27 = getelementptr inbounds nuw i32, ptr %5, i64 %23
  %28 = load i32, ptr %27, align 4
  %29 = shl nsw i32 %28, 1
  %30 = getelementptr inbounds nuw i32, ptr %14, i64 %23
  store i32 %29, ptr %30, align 4
  %31 = add nuw i64 %23, 1
  %32 = icmp eq i64 %31, %19
  br i1 %32, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z12v_rev_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v_rev_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = icmp eq ptr %6, %4
  br i1 %7, label %bb22, label %bb8

bb8:                                                ; preds = %entry
  %9 = ptrtoint ptr %6 to i64
  %10 = ptrtoint ptr %4 to i64
  %11 = sub i64 %9, %10
  %12 = ashr exact i64 %11, 2
  %13 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %14 = load ptr, ptr %13, align 8
  %15 = ptrtoint ptr %14 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = add nsw i64 %12, -1
  %20 = icmp ult i64 %19, %18
  br label %bb23

bb21:                                               ; preds = %bb26
  br label %bb22

bb22:                                               ; preds = %bb21, %entry
  ret void

bb23:                                               ; preds = %bb8, %bb26
  %24 = phi i64 [ %27, %bb26 ], [ %12, %bb8 ]
  br i1 %20, label %bb26, label %bb25

bb25:                                               ; preds = %bb23
  tail call void @llvm.trap()
  unreachable

bb26:                                               ; preds = %bb23
  %27 = add i64 %24, -1
  %28 = getelementptr inbounds nuw i32, ptr %4, i64 %27
  %29 = load i32, ptr %28, align 4
  %30 = shl nsw i32 %29, 1
  %31 = getelementptr inbounds nuw i32, ptr %3, i64 %27
  store i32 %30, ptr %31, align 4
  %32 = icmp eq i64 %27, 0
  br i1 %32, label %bb21, label %bb23
}


; *** IR Dump Before LoopVectorizePass on _Z12v_fwd_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v_fwd_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = ptrtoint ptr %6 to i64
  %8 = ptrtoint ptr %3 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %12 = load ptr, ptr %11, align 8
  %13 = icmp eq ptr %12, %4
  br i1 %13, label %bb21, label %bb14

bb14:                                               ; preds = %entry
  %15 = ptrtoint ptr %12 to i64
  %16 = ptrtoint ptr %4 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %18, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb26
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb14, %bb26
  %23 = phi i64 [ %31, %bb26 ], [ 0, %bb14 ]
  %24 = icmp eq i64 %23, %10
  br i1 %24, label %bb25, label %bb26

bb25:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb26:                                               ; preds = %bb22
  %27 = getelementptr inbounds nuw i32, ptr %4, i64 %23
  %28 = load i32, ptr %27, align 4
  %29 = shl nsw i32 %28, 1
  %30 = getelementptr inbounds nuw i32, ptr %3, i64 %23
  store i32 %29, ptr %30, align 4
  %31 = add nuw i64 %23, 1
  %32 = icmp eq i64 %31, %19
  br i1 %32, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z7v_rev_jRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z7v_rev_jRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %1, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = icmp eq ptr %4, %5
  br i1 %10, label %bb21, label %bb11

bb11:                                               ; preds = %entry
  %12 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %0, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %9, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb31
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb11, %bb31
  %23 = phi i64 [ 0, %bb11 ], [ %36, %bb31 ]
  %24 = xor i64 %23, -1
  %25 = add i64 %9, %24
  %26 = icmp ult i64 %25, %9
  br i1 %26, label %bb28, label %bb27

bb27:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb28:                                               ; preds = %bb22
  %29 = icmp ult i64 %25, %18
  br i1 %29, label %bb31, label %bb30

bb30:                                               ; preds = %bb28
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb28
  %32 = getelementptr inbounds nuw i32, ptr %5, i64 %25
  %33 = load i32, ptr %32, align 4
  %34 = shl nsw i32 %33, 1
  %35 = getelementptr inbounds nuw i32, ptr %14, i64 %25
  store i32 %34, ptr %35, align 4
  %36 = add nuw i64 %23, 1
  %37 = icmp eq i64 %36, %19
  br i1 %37, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z8v_s2_preRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z8v_s2_preRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %11 = load ptr, ptr %10, align 8
  %12 = load ptr, ptr %1, align 8
  %13 = ptrtoint ptr %11 to i64
  %14 = ptrtoint ptr %12 to i64
  %15 = sub i64 %13, %14
  %16 = ashr exact i64 %15, 2
  %17 = lshr i64 %16, 1
  %18 = icmp ult i64 %17, %9
  br i1 %18, label %bb23, label %bb19

bb19:                                               ; preds = %entry
  %20 = icmp eq ptr %4, %5
  br i1 %20, label %bb25, label %bb21

bb21:                                               ; preds = %bb19
  %22 = call i64 @llvm.umax.i64(i64 %9, i64 1)
  br label %bb26

bb23:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb24:                                               ; preds = %bb35
  br label %bb25

bb25:                                               ; preds = %bb24, %bb19
  ret void

bb26:                                               ; preds = %bb21, %bb35
  %27 = phi i64 [ %42, %bb35 ], [ 0, %bb21 ]
  %28 = shl nuw i64 %27, 1
  %29 = icmp ult i64 %28, %16
  br i1 %29, label %bb31, label %bb30

bb30:                                               ; preds = %bb26
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb26
  %32 = or disjoint i64 %28, 1
  %33 = icmp ult i64 %32, %16
  br i1 %33, label %bb35, label %bb34

bb34:                                               ; preds = %bb31
  tail call void @llvm.trap()
  unreachable

bb35:                                               ; preds = %bb31
  %36 = getelementptr inbounds nuw i32, ptr %12, i64 %28
  %37 = load i32, ptr %36, align 4
  %38 = getelementptr inbounds nuw i32, ptr %12, i64 %32
  %39 = load i32, ptr %38, align 4
  %40 = add nsw i32 %39, %37
  %41 = getelementptr inbounds nuw i32, ptr %5, i64 %27
  store i32 %40, ptr %41, align 4
  %42 = add nuw i64 %27, 1
  %43 = icmp eq i64 %42, %22
  br i1 %43, label %bb24, label %bb26
}


; *** IR Dump Before LoopVectorizePass on _Z12v_s2_pre_mulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z12v_s2_pre_mulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = icmp sgt i64 %9, -1
  br i1 %10, label %bb11, label %bb25

bb11:                                               ; preds = %entry
  %12 = lshr exact i64 %8, 1
  %13 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %14 = load ptr, ptr %13, align 8
  %15 = load ptr, ptr %1, align 8
  %16 = ptrtoint ptr %14 to i64
  %17 = ptrtoint ptr %15 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = icmp ugt i64 %12, %19
  br i1 %20, label %bb25, label %bb21

bb21:                                               ; preds = %bb11
  %22 = icmp eq ptr %4, %5
  br i1 %22, label %bb27, label %bb23

bb23:                                               ; preds = %bb21
  %24 = call i64 @llvm.umax.i64(i64 %9, i64 1)
  br label %bb28

bb25:                                               ; preds = %bb11, %entry
  tail call void @llvm.trap()
  unreachable

bb26:                                               ; preds = %bb37
  br label %bb27

bb27:                                               ; preds = %bb26, %bb21
  ret void

bb28:                                               ; preds = %bb23, %bb37
  %29 = phi i64 [ %44, %bb37 ], [ 0, %bb23 ]
  %30 = shl nuw i64 %29, 1
  %31 = icmp ult i64 %30, %19
  br i1 %31, label %bb33, label %bb32

bb32:                                               ; preds = %bb28
  tail call void @llvm.trap()
  unreachable

bb33:                                               ; preds = %bb28
  %34 = or disjoint i64 %30, 1
  %35 = icmp ult i64 %34, %19
  br i1 %35, label %bb37, label %bb36

bb36:                                               ; preds = %bb33
  tail call void @llvm.trap()
  unreachable

bb37:                                               ; preds = %bb33
  %38 = getelementptr inbounds nuw i32, ptr %15, i64 %30
  %39 = load i32, ptr %38, align 4
  %40 = getelementptr inbounds nuw i32, ptr %15, i64 %34
  %41 = load i32, ptr %40, align 4
  %42 = add nsw i32 %41, %39
  %43 = getelementptr inbounds nuw i32, ptr %5, i64 %29
  store i32 %42, ptr %43, align 4
  %44 = add nuw i64 %29, 1
  %45 = icmp eq i64 %44, %24
  br i1 %45, label %bb26, label %bb28
}


; *** IR Dump Before LoopVectorizePass on _Z9v_s2_spanRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z9v_s2_spanRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = icmp sgt i64 %9, -1
  br i1 %10, label %bb12, label %bb11

bb11:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb12:                                               ; preds = %entry
  %13 = load ptr, ptr %1, align 8
  %14 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %15 = load ptr, ptr %14, align 8
  %16 = ptrtoint ptr %15 to i64
  %17 = ptrtoint ptr %13 to i64
  %18 = sub i64 %16, %17
  %19 = ashr exact i64 %18, 2
  %20 = lshr exact i64 %8, 1
  %21 = icmp ugt i64 %20, %19
  br i1 %21, label %bb22, label %bb23

bb22:                                               ; preds = %bb12
  tail call void @llvm.trap()
  unreachable

bb23:                                               ; preds = %bb12
  %24 = icmp eq ptr %4, %5
  %25 = icmp ne ptr %13, null
  %26 = or i1 %24, %25
  br i1 %26, label %bb27, label %bb30

bb27:                                               ; preds = %bb23
  br i1 %24, label %bb32, label %bb28

bb28:                                               ; preds = %bb27
  %29 = call i64 @llvm.umax.i64(i64 %9, i64 1)
  br label %bb33

bb30:                                               ; preds = %bb23
  tail call void @llvm.trap()
  unreachable

bb31:                                               ; preds = %bb39
  br label %bb32

bb32:                                               ; preds = %bb31, %bb27
  ret void

bb33:                                               ; preds = %bb28, %bb39
  %34 = phi i64 [ %46, %bb39 ], [ 0, %bb28 ]
  %35 = shl nuw i64 %34, 1
  %36 = or disjoint i64 %35, 1
  %37 = icmp ult i64 %36, %20
  br i1 %37, label %bb39, label %bb38

bb38:                                               ; preds = %bb33
  tail call void @llvm.trap()
  unreachable

bb39:                                               ; preds = %bb33
  %40 = getelementptr inbounds nuw i32, ptr %13, i64 %35
  %41 = load i32, ptr %40, align 4
  %42 = getelementptr inbounds nuw i32, ptr %13, i64 %36
  %43 = load i32, ptr %42, align 4
  %44 = add nsw i32 %43, %41
  %45 = getelementptr inbounds nuw i32, ptr %5, i64 %34
  store i32 %44, ptr %45, align 4
  %46 = add nuw i64 %34, 1
  %47 = icmp eq i64 %46, %29
  br i1 %47, label %bb31, label %bb33
}


; *** IR Dump Before LoopVectorizePass on _Z8v_s2_rawRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z8v_s2_rawRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = ptrtoint ptr %4 to i64
  %7 = ptrtoint ptr %5 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 2
  %10 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %11 = load ptr, ptr %10, align 8
  %12 = load ptr, ptr %1, align 8
  %13 = ptrtoint ptr %11 to i64
  %14 = ptrtoint ptr %12 to i64
  %15 = sub i64 %13, %14
  %16 = ashr exact i64 %15, 2
  %17 = lshr i64 %16, 1
  %18 = icmp ult i64 %17, %9
  br i1 %18, label %bb23, label %bb19

bb19:                                               ; preds = %entry
  %20 = icmp eq ptr %4, %5
  br i1 %20, label %bb25, label %bb21

bb21:                                               ; preds = %bb19
  %22 = call i64 @llvm.umax.i64(i64 %9, i64 1)
  br label %bb26

bb23:                                               ; preds = %entry
  tail call void @llvm.trap()
  unreachable

bb24:                                               ; preds = %bb26
  br label %bb25

bb25:                                               ; preds = %bb24, %bb19
  ret void

bb26:                                               ; preds = %bb21, %bb26
  %27 = phi i64 [ %36, %bb26 ], [ 0, %bb21 ]
  %28 = shl nuw i64 %27, 1
  %29 = getelementptr inbounds nuw i32, ptr %12, i64 %28
  %30 = load i32, ptr %29, align 4
  %31 = or disjoint i64 %28, 1
  %32 = getelementptr inbounds nuw i32, ptr %12, i64 %31
  %33 = load i32, ptr %32, align 4
  %34 = add nsw i32 %33, %30
  %35 = getelementptr inbounds nuw i32, ptr %5, i64 %27
  store i32 %34, ptr %35, align 4
  %36 = add nuw nsw i64 %27, 1
  %37 = icmp eq i64 %36, %22
  br i1 %37, label %bb24, label %bb26
}


; *** IR Dump Before LoopVectorizePass on _Z11v_s2_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z11v_s2_manualRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = load ptr, ptr %1, align 8
  %5 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = ptrtoint ptr %6 to i64
  %8 = ptrtoint ptr %4 to i64
  %9 = sub i64 %7, %8
  %10 = ashr exact i64 %9, 2
  %11 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %12 = load ptr, ptr %11, align 8
  %13 = icmp eq ptr %12, %3
  br i1 %13, label %bb21, label %bb14

bb14:                                               ; preds = %entry
  %15 = ptrtoint ptr %12 to i64
  %16 = ptrtoint ptr %3 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %18, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb28
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb14, %bb28
  %23 = phi i64 [ %35, %bb28 ], [ 0, %bb14 ]
  %24 = shl i64 %23, 1
  %25 = or disjoint i64 %24, 1
  %26 = icmp ult i64 %25, %10
  br i1 %26, label %bb28, label %bb27

bb27:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb28:                                               ; preds = %bb22
  %29 = getelementptr inbounds nuw i32, ptr %4, i64 %24
  %30 = load i32, ptr %29, align 4
  %31 = getelementptr inbounds nuw i32, ptr %4, i64 %25
  %32 = load i32, ptr %31, align 4
  %33 = add nsw i32 %32, %30
  %34 = getelementptr inbounds nuw i32, ptr %3, i64 %23
  store i32 %33, ptr %34, align 4
  %35 = add nuw i64 %23, 1
  %36 = icmp eq i64 %35, %19
  br i1 %36, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z8v_s2_oneRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z8v_s2_oneRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = load ptr, ptr %0, align 8
  %6 = icmp eq ptr %4, %5
  br i1 %6, label %bb21, label %bb7

bb7:                                                ; preds = %entry
  %8 = ptrtoint ptr %4 to i64
  %9 = ptrtoint ptr %5 to i64
  %10 = sub i64 %8, %9
  %11 = ashr exact i64 %10, 2
  %12 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %1, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  %19 = call i64 @llvm.umax.i64(i64 %11, i64 1)
  br label %bb22

bb20:                                               ; preds = %bb27
  br label %bb21

bb21:                                               ; preds = %bb20, %entry
  ret void

bb22:                                               ; preds = %bb7, %bb27
  %23 = phi i64 [ 0, %bb7 ], [ %31, %bb27 ]
  %24 = shl i64 %23, 1
  %25 = icmp ult i64 %24, %18
  br i1 %25, label %bb27, label %bb26

bb26:                                               ; preds = %bb22
  tail call void @llvm.trap()
  unreachable

bb27:                                               ; preds = %bb22
  %28 = getelementptr inbounds nuw i32, ptr %14, i64 %24
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr inbounds nuw i32, ptr %5, i64 %23
  store i32 %29, ptr %30, align 4
  %31 = add nuw i64 %23, 1
  %32 = icmp eq i64 %31, %19
  br i1 %32, label %bb20, label %bb22
}


; *** IR Dump Before LoopVectorizePass on _Z6v_s2_jRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ ***
; Function Attrs: mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable
define dso_local void @_Z6v_s2_jRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_(ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %0, ptr nocapture noundef nonnull readonly align 8 dereferenceable(24) %1) local_unnamed_addr #0 {
entry:
  %3 = load ptr, ptr %0, align 8
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %5 = load ptr, ptr %4, align 8
  %6 = ptrtoint ptr %5 to i64
  %7 = ptrtoint ptr %3 to i64
  %8 = sub i64 %6, %7
  %9 = ashr exact i64 %8, 1
  %10 = icmp eq ptr %5, %3
  br i1 %10, label %bb20, label %bb11

bb11:                                               ; preds = %entry
  %12 = getelementptr inbounds nuw i8, ptr %1, i64 8
  %13 = load ptr, ptr %12, align 8
  %14 = load ptr, ptr %1, align 8
  %15 = ptrtoint ptr %13 to i64
  %16 = ptrtoint ptr %14 to i64
  %17 = sub i64 %15, %16
  %18 = ashr exact i64 %17, 2
  br label %bb21

bb19:                                               ; preds = %bb29
  br label %bb20

bb20:                                               ; preds = %bb19, %entry
  ret void

bb21:                                               ; preds = %bb11, %bb29
  %22 = phi i64 [ 0, %bb11 ], [ %37, %bb29 ]
  %23 = icmp ult i64 %22, %18
  br i1 %23, label %bb25, label %bb24

bb24:                                               ; preds = %bb21
  tail call void @llvm.trap()
  unreachable

bb25:                                               ; preds = %bb21
  %26 = or disjoint i64 %22, 1
  %27 = icmp ult i64 %26, %18
  br i1 %27, label %bb29, label %bb28

bb28:                                               ; preds = %bb25
  tail call void @llvm.trap()
  unreachable

bb29:                                               ; preds = %bb25
  %30 = getelementptr inbounds nuw i32, ptr %14, i64 %22
  %31 = load i32, ptr %30, align 4
  %32 = getelementptr inbounds nuw i32, ptr %14, i64 %26
  %33 = load i32, ptr %32, align 4
  %34 = add nsw i32 %33, %31
  %35 = lshr exact i64 %22, 1
  %36 = getelementptr inbounds nuw i32, ptr %3, i64 %35
  store i32 %34, ptr %36, align 4
  %37 = add nuw i64 %22, 2
  %38 = icmp ult i64 %37, %9
  br i1 %38, label %bb21, label %bb19
}

attributes #0 = { mustprogress noinline nounwind memory(readwrite, inaccessiblemem: write) uwtable }
attributes #9999 = { cold noreturn nounwind memory(inaccessiblemem: write) }
